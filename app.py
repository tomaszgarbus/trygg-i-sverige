from dash import Dash, html, dcc, dash_table
import plotly.graph_objects as go
import plotly.express as px
from xls_utils import default_crime_exposure_table
import pandas as pd
import itertools

app = Dash(__name__)
data = default_crime_exposure_table()
numeric_columns = [{
    'id': col,
    'name': col,
    'type':'numeric',
    'format': {
        'specifier': '.2f'
    }
} for col in data.columns]
columns = [{
    'id': 'Plats',
    'name': 'Plats'
}] + numeric_columns

def discrete_color_background_bins(df: pd.DataFrame, column: str) -> dict:
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


def build_tooltip(value: any, row: dict, column: dict, df: pd.DataFrame) -> str:
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


data_dict = data.reset_index(names='Plats').to_dict('records', index=True)
tooltip_data = [
        {
            column: {
                'value': build_tooltip(value, row, column, data),
                'type': 'markdown'
            }
            for column, value in row.items()
        } for row in data_dict
    ]

app.layout = html.Div([
    html.H1(
        'Utsatthet för brott i år 2020-2021'
    ),
    'TODO list:',
    html.Ul(
        [
            html.Li('Good tooltips'),
            html.Li('Filter cities/counties/all'),
            html.Li('Apply filtering rules to computed tooltips'),
            html.Li('Separate tab for table 3.x series'),
            html.Li('Show ranking number row'),
            html.Li('Use Bootstrap 5 for styling'),
            html.Li('Center everything'),
        ]
    ),
    dash_table.DataTable(
        data=data_dict,
        columns=columns,
        tooltip_data=tooltip_data,
        sort_action="native",
        page_size = 400,
        style_data_conditional=list(itertools.chain.from_iterable([
            discrete_color_background_bins(data, col['name'])
            for col in numeric_columns
        ])),
        css=[{'selector': 'table', 'rule': 'table-layout: fixed'}],
        style_cell={
            'white-space': 'normal',
            'height': 'auto',
            'overflow-wrap': 'break-word',
            'word-break': 'break-all'
            # 'overflow': 
        },
    )
], style={
    'width': '80%'
})

if __name__ == '__main__':
    app.run(debug=True)