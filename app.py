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

intro = html.Div([
    html.P('Avsnittet om utsatthet för brott omfattar följande brottstyper:'),
    html.Ul([
        html.Li(['brott mot enskild person:',
          html.Ul([
              html.Li('kort-/kreditbedrägeri'),
              html.Li('försäljningsbedrägeri'),
              html.Li('fickstöld'),
              html.Li('personrån'),
              html.Li('sexualbrott'),
              html.Li('misshandel'),
              html.Li('hot'),
              html.Li('trakasserier'),
              html.Li('nätkränkning'),
          ])
        ]),
        html.Li(['egendomsbrott mot hushåll:',
            html.Ul([
                html.Li('cykelstöld'),
                html.Li('bilstöld'),
                html.Li('stöld ur eller från fordon'),
                html.Li('bostadsinbrott'),
            ])
        ])
    ])
])

app.layout = html.Div([
    'TODO list:',
    html.Ul(
        [
            html.Li('Show ranking number row'),
            html.Li('Allow to collapse subcategories on the table'),
            html.Li('Fix table size to be 100% height'),
        ]
    ),
    intro,
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
    app.run(debug=True)