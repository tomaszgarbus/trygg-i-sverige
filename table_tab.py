"""
Dash tab for table of series 2.x or 3.x
"""
import pandas as pd
from dash import Dash, html, dcc, dash_table
import itertools
import plotly.express as px

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


def _build_tooltip(value: any, row: dict, column: dict, df: pd.DataFrame) -> str:
    """Produces tooltip markdown for a single cell."""
    if type(value) == float:
        nlt = df[df[column] < value][column].size
        neq = df[df[column] == value][column].size
        ngt = df[df[column] > value][column].size
        rank = ngt + neq
        all = nlt + neq + ngt
        return (
            f"**{row['Plats']} / {column.strip()}**\n"
            f"{rank}. farligaste av {all}\n"
        )
    else:
        return f"**{row['Plats']}**"


class TableTab:
    def __init__(self, data: pd.DataFrame, header: str):
        self._header = header
        self._data = data
        self._numeric_columns = [{
            'id': col,
            'name': col,
            'type':'numeric',
            'format': {
                'specifier': '.2f'
            }
        } for col in self._data]
        self._columns = [{
            'id': 'Plats',
            'name': 'Plats'
        }] + self._numeric_columns
        self._data_dict = self._data.reset_index(names='Plats').to_dict(
            'records', index=True)
        self._tooltip_data = [
                {
                    column: {
                        'value': _build_tooltip(value, row, column, data),
                        'type': 'markdown'
                    }
                    for column, value in row.items()
                } for row in self._data_dict
            ]
    
    def _build_data_table(self) -> dash_table.DataTable:
        """Constructs the DataTable for this tab."""
        return dash_table.DataTable(
            data=self._data_dict,
            columns=self._columns,
            tooltip_data=self._tooltip_data,
            sort_action="native",
            page_size = 400,
            style_data_conditional=list(itertools.chain.from_iterable([
                _discrete_color_background_bins(self._data, col['name'])
                for col in self._numeric_columns
            ])),
            css=[{'selector': 'table', 'rule': 'table-layout: fixed'}],
            style_cell={
                'white-space': 'normal',
                'height': 'auto',
                'overflow-wrap': 'break-word',
                'word-break': 'break-all'
            },
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
            self._build_data_table()
        ])