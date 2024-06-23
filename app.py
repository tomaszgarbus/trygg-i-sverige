from dash import Dash, html, dcc
from table_tab import TableTab
from xls_utils import default_crime_exposure_table, default_crime_fear_table

app = Dash(__name__)
tab2x = TableTab(
    default_crime_exposure_table(),
    'utsatthet',
    'Utsatthet för brott i år 2020-2021'
)
tab3x = TableTab(
    default_crime_fear_table(),
    'otrygghet',
    'Otrygghet och oro för brott i år 2021-2022'
)

app.layout = html.Div([
    'TODO list:',
    html.Ul(
        [
            html.Li('Show ranking number row'),
            html.Li('Fix table size to be 100% height'),
        ]
    ),
    dcc.Tabs([
        dcc.Tab([
            tab2x.build_tab_contents()
        ],
        label=tab2x.label()),
        dcc.Tab([
            tab3x.build_tab_contents()
        ],
        label=tab3x.label()),
    ])
], style={
    'width': '96%',
    'margin': 'auto'
})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False)