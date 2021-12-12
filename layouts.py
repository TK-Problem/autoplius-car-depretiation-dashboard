from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd


header = html.Header(
    dbc.Row(
        [
            dbc.Col(
                [
                    html.Img(id="logo-image", src='assets/app_logo.png',  height='100px'),
                ],
                width={"size": 3},
            ),
        ],
    ),
    className='card text-white bg-dark mb-3'
)


footer = html.Footer(
    dbc.Row(
        dbc.Col(
            [
                html.Div("Sukurta Tomo Uždavinio", style={'textAlign': 'center'}),
                html.Div("t.uzdavinys@gmail.com", style={'textAlign': 'center'}),
                html.P("Projektas dar nebaigtas.", style={'textAlign': 'center'})
            ],
            width={"size": 6, "offset": 3},
        ),
    ),
    className='card text-white bg-dark mb-3'
)

# first basic DataFrame for better performance
_df = pd.DataFrame({'Year': [2020, 2021, 2020, 2021],
                    'Price': [10000, 20000, 30000, 40000],
                    'Range': ['Low', 'Low', 'High', 'High']})


tab1_content = dbc.Card(
                dbc.CardBody(
                    [
                        html.H4("Pagaminimo metai", className="card-title"),
                        dcc.Dropdown(id='car-year-drop-menu', options=[], value='year', clearable=False,
                                     placeholder="Pasirinkite mašinos pagaminimo metus"),
                        html.Br(),
                        html.P('', id="deval-chart-description", className="tab-text"),
                        # generate random graph for better performance
                        dcc.Graph(figure=px.line(_df, x="Year", y="Price", color='Range'),
                                  id="tab-1-deval-chart", config={'displayModeBar': False, 'responsive': False}),
                        html.Br(),
                        dbc.Button(
                                    "Rodyti originalų autoplius grafiką",
                                    id="image-collapse-button",
                                    className="btn btn-dark"
                                ),

                        dbc.Collapse(
                                    [html.Br(),
                                     html.Img(id='deval-auto-plius-img', src='', style={'width': '100%'})],
                                    id="png-collapse",
                                    is_open=False,
                        ),
                    ]
                ),
                className="mt-3",
)

tab2_content = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Kainos metiniai pokyčiai", className="card-title"),
            html.P("Iš surinktų autoplius duomenų mes negalime įvertinti kainų rėžių tikslumo. Dižiausia X metų kaina "
                   "galėjo būti išskaičiuota iš 1 skelbimo arba iš >100. Mes geriausiu atveju galime įvertinti kainos "
                   "kritimo tendenciją, kurią apskaičiuojau kainos pokyčių medianos.", className="card-text"),
            dcc.Graph(id="tab-2-deval-chart", config={'displayModeBar': False, 'responsive': False}),
            dbc.Button("Pakeisti grafiko tipą", id="tab-2-change-graph-type-btn",
                       className="btn btn-dark", n_clicks=0),
            html.Hr(),
            html.P("Šią tendenciją galime palyginti su visų X gamintojo automobilių vidutinę kainos kitimo tendenciją "
                   "ir visų automobilių kitimo tendencija.", id='tab-2-chart-fig-des', className="card-text"),
        ]
    ),
    className="mt-3",
)


tab3_content = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Duomenų įvedimas", className="card-title"),
            html.P("Laikinas tekstas", className="card-text"),
            html.H3("Tiesinis modelis #1", className="card-title"),
            html.P("Apskaičiuoja vidutinę kainos nuvertėjimą iš:", className="card-text")
        ]
    ),
    className="mt-3",
)

tabs_layout = dbc.Collapse(
    html.Div(
        [
            dcc.Tabs(id="tabs-example-graph",
                     value='tab-1',
                     children=[

                         dcc.Tab(label='Kainų kitimas', children=[tab1_content], value='tab-1'),
                         dcc.Tab(label='Nuvertėjimo tendencijos', children=[tab2_content], value='tab-2'),
                         dcc.Tab(label='Kainos įvertinimas', children=[tab3_content], value='tab-3')

                                ]),
            html.Br(),
          ]
    ), id="tabs-collapse", is_open=False)
