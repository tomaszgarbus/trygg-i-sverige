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
        ])
    ])
    # """
    #   Avsnittet om utsatthet för brott omfattar följande brottstyper:
    #   • brott mot enskild person:
    #   - kort-/kreditbedrägeri
    #   - försäljningsbedrägeri
    #   - fickstöld
    #   - personrån
    #   - sexualbrott
    #   - misshandel
    #   - hot
    #   - trakasserier10
    #   - nätkränkning
    #   • egendomsbrott mot hushåll:
    #   - cykelstöld
    #   - bilstöld
    #   - stöld ur eller från fordon
    #   - bostadsinbrott"""
])

app.layout = html.Div([
    'TODO list:',
    html.Ul(
        [
            html.Li('Show city sizes in tooltips'),
            html.Li('Filter cities/counties/all'),
            html.Li('Filter by city sizes'),
            html.Li('Apply filtering rules to computed tooltips'),
            html.Li('Separate tab for table 3.x series'),
            html.Li('Show ranking number row'),
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