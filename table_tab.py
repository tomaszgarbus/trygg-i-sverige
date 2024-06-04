"""
Dash tab for table of series 2.x or 3.x
"""
import pandas as pd
from dash import html, dash_table, Input, Output, callback, dcc
import itertools
import plotly.express as px

# Label for the row with overall country-wide stats.
_TOTAL_ROW_LABEL = 'SAMTLIGA (16–84 år)'

def _discrete_color_background_bins(df: pd.DataFrame, column: str) -> dict:
    """Builds the conditional style for column.

    Returns the style which can be plugged into style_data_conditional on the
    DataTable built from df.
    """
    min_val = df[column].min()
    max_val = df[column].max()
    colors = px.colors.sequential.Oranges
    nbins = len(colors)
    ranges = [
        ((max_val - min_val) * i / nbins) + min_val
        for i in range(nbins)
    ]
    styles = []
    for i in range(1, nbins):
        bg_color = colors[i-1]
        color = 'white' if i > nbins / 2. else 'inherit'
        styles.append({
                'if': {
                    'filter_query': (
                        '{{{column}}} >= {min_bound}' +
                        (' && {{{column}}} < {max_bound}'
                         if (i < nbins - 1) else '')
                    ).format(column=column, min_bound=ranges[i-1], max_bound=ranges[i]),
                    'column_id': column
                },
                'background-color': bg_color,
                'color': color,
            })
    return styles

def _bold_text_in_summary_row() -> dict:
    """Builds a conditional style for the "SAMTLIGA" column.
    """
    return {
        'if': {
            'row_index': 0
        },
        'font-weight': 'bold'
    }

class TableTab:
    def __init__(self, data: pd.DataFrame, table_id: str, header: str):
        self._all_data = data
        self._data = data
        self._table_id = table_id
        self._header = header
        self._tooltip_cache = {}
        self._recompute()
        self._register_sort_callback()

    def _county_data(self) -> pd.DataFrame:
        """Filters self._data to leave only counties."""
        return self._all_data[self._all_data.index.str.contains(
            'län$'
        )]

    def _district_data(self) -> pd.DataFrame:
        """Filters self._data to include only districts of Stockholm."""
        return self._all_data[
            self._all_data.index.str.contains('Stadsdelsomr.')
        ]
    
    def _city_data(self) -> pd.DataFrame:
        """Filters self._data to include only cities."""
        return self._all_data[
            ~self._all_data.index.str.contains(
                '(SAMTLIGA)|(län$)|(Stadsdelsomr.)')
        ]
    
    def _get_selected_data(self, selection: str) -> pd.DataFrame:
        """Gets selected data from the checkbox value"""
        return {
            'Counties': self._county_data,
            'Stockholm Districts': self._district_data,
            'Cities': self._district_data
        }[selection]()

    def _build_tooltip(
            self, value: any, row: dict, column: dict,
            invalidate_cache = False) -> str:
        """Produces tooltip markdown for a single cell."""
        key = row['Plats'], column
        if invalidate_cache:
            self._tooltip_cache.pop(key)
        if key not in self._tooltip_cache:
          if type(value) == float:
              nlt = self._data[self._data[column] < value][column].size
              neq = self._data[self._data[column] == value][column].size
              ngt = self._data[self._data[column] > value][column].size
              rank = ngt + neq
              all = nlt + neq + ngt
              self._tooltip_cache[key] = (
                  f"**{row['Plats']} / {column.strip()}**\n"
                  f"{rank}. farligaste av {all}\n"
              )
          else:
              self._tooltip_cache[key] = f"**{row['Plats']}**"
        return self._tooltip_cache[key]

    def _recompute(self, invalidate_tooltip_cache = False):
        """Recomputes all cached values and aggregations from data."""
        self._numeric_columns = [{
            'id': col,
            'name': col,
            'type':'numeric',
            'format': {
                'specifier': '.2f'
            }
        } for col in self._all_data]
        self._columns = [{
            'id': 'Plats',
            'name': 'Plats'
        }] + self._numeric_columns
        self._data_dict = self._data.reset_index(names='Plats').to_dict(
            'records', index=True)
        self._tooltip_data = [
            {
                column: {
                    'value': self._build_tooltip(
                        value, row, column, invalidate_tooltip_cache),
                    'type': 'markdown'
                }
                for column, value in row.items()
            } for row in self._data_dict
        ]

    def _update_table(self, sort_by, filters):
        print(filters)
        # First apply filtering.
        selected_data = [
            # Country-wide-summary
            self._data[self._data.index == _TOTAL_ROW_LABEL],
        ] + [self._get_selected_data(s) for s in filters]
        self._data = pd.concat(selected_data)
        # Now apply sorting.
        if sort_by:
            # Don't sort the first row ("SAMTLIGA").
            self._data = pd.concat([
                # Row 0:
                self._data[self._data.index == _TOTAL_ROW_LABEL],
                # Rows 1:
                self._data[self._data.index != _TOTAL_ROW_LABEL].sort_values(
                    sort_by[0]['column_id'],
                    ascending=sort_by[0]['direction'] == 'asc',
                    inplace=False
                )
            ])
            self._recompute()
        return self._data_dict, self._tooltip_data
    
    def _register_sort_callback(self) -> None:
        self._sort_callback = callback(
            Output(self._table_id, 'data'),
            Output(self._table_id, 'tooltip_data'),
            Input(self._table_id, 'sort_by'),
            Input(f'{self._table_id}_filters', 'value'),
        )(self._update_table)

    def _build_data_table(self) -> dash_table.DataTable:
        """Constructs the DataTable for this tab."""
        return dash_table.DataTable(
            id=self._table_id,
            data=self._data_dict,
            columns=self._columns,
            tooltip_data=self._tooltip_data,
            sort_action="custom",
            page_size = 400,
            style_data_conditional=list(itertools.chain.from_iterable([
                _discrete_color_background_bins(self._data, col['name'])
                for col in self._numeric_columns
            ])) + [_bold_text_in_summary_row()],
            # css=[
            #     {'selector': '.dash-table-container', 'rule': 'height: 100% !important;'},
            # ],
            style_cell={
                'white-space': 'normal',
                'height': 'auto',
                'width': 90,
                'overflow-wrap': 'break-word',
                'word-break': 'break-all'
            },
            style_table={
                # TODO: Make it 100% instead
                'height': 800,
                'max-height': '100%'
            },
            fixed_rows={
                'headers': True,
                'data': 1,
            },
            style_header={
                'font-weight': 'bold'
            }
        )

    def label(self) -> str:
        """Displayable label on the tabs list."""
        return self._header

    def build_tab_contents(self) -> html.Div:
        """Builds displayable html node."""
        return html.Div([
            html.H1(
                self._header
            ),
            dcc.Checklist(
                options=['Counties', 'Stockholm Districts', 'Cities'],
                value=['Counties', 'Stockholm Districts', 'Cities'],
                id=f'{self._table_id}_filters'
            ),
            self._build_data_table()
        ])