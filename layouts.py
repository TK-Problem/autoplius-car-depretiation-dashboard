from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

header = html.Header(
    dbc.Row(
        [
            dbc.Col(
                [
                    html.Img(id="logo-image", src='assets/app_logo.png', height='100px'),
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
            html.P("Šią tendenciją galime palyginti su visų X gamintojo automobilių vidutinę kainos kitimo tendenciją "
                   "ir visų automobilių kitimo tendencija.", id='tab-2-chart-fig-des', className="card-text"),
            html.Hr(),
            dbc.RadioItems(id="tab-2-radio-items", value='MODEL',
                           options=[{'label': 'Pasirinktas modelis', 'value': 'MODEL'},
                                    {'label': 'Visi gamintojo modeliai', 'value': 'MANU'}],
                           labelCheckedClassName="text-secondary",
                           inputCheckedClassName="border border-primary bg-primary"),
            html.Hr(),
            dcc.Graph(id="tab-2-deval-chart", config={'displayModeBar': False, 'responsive': False}),
            dbc.Button("Pakeisti grafiko tipą", id="tab-2-change-graph-type-btn",
                       className="btn btn-dark", n_clicks=0),
            html.Hr(),
            html.H4("Nuvertėjimo skaičiuoklė", className="card-title"),
            html.Div(
                dbc.Select(id="tab-2-year-select", style={'text-align': 'right'}, options=[],
                           placeholder='Pagaminimo metai'),
                className='input-group mb-3', style={'width': '310px'}),
            html.Div(
                [
                    dbc.FormFloating(
                        [
                            dbc.Input(id='tab-2-price', placeholder="10000",
                                      type="number", min=5000, max=100000, step=100,
                                      style={'text-align': 'right'}),
                            dbc.Label("Automobilio kaina"),
                        ]
                    ),
                    html.Span("€", className='input-group-text'),
                ]
                , className='input-group mb-3'),

            html.Div("Tekstas", id='tab-2-price_check', className='invalid-feedback'),
            dbc.Button("Skaičiuoti", id="tab-2-calcualte-deval-btn", className="btn btn-dark",
                       n_clicks=0, disabled=True),
            dbc.Collapse(
                [
                    html.Br(),
                    dcc.Markdown(children='', id='markdown-text'),
                    dcc.Graph(id="tab-2-calc-chart", config={'displayModeBar': False, 'responsive': False}),
                ],
                id="deval-calculation-results-collapse",
                is_open=False,
            ),
        ]
    ),
    className="mt-3",
)

# tab3_content = dbc.Card(
#     dbc.CardBody(
#         [
#             html.H4("Pagaminimo metai", className="card-title"),
#             dcc.Dropdown(id='car-year-drop-msenu', options=[], value='year', clearable=False,
#                          placeholder="Pasirinkite mašinos pagaminimo metus"),
#             html.Br(),
#             dcc.Slider(id='car-year-slider', min=1, max=10, step=1, value=1,
#                        marks={year: str(year) for year in range(1, 11)}),
#             html.H4("Duomenų įvedimas", className="card-title"),
#             html.P("Laikinas tekstas", className="card-text"),
#             html.H3("Tiesinis modelis #1", className="card-title"),
#             html.P("Apskaičiuoja vidutinę kainos nuvertėjimą iš:", className="card-text")
#         ]
#     ),
#     className="mt-3",
# )

tabs_layout = dbc.Collapse(
    html.Div(
        [
            dcc.Tabs(id="tabs-example-graph",
                     value='tab-1',
                     children=[

                         dcc.Tab(label='Kainų kitimas', children=[tab1_content], value='tab-1'),
                         dcc.Tab(label='Nuvertėjimo tendencijos', children=[tab2_content], value='tab-2'),
                         # dcc.Tab(label='Kainos įvertinimas', children=[tab3_content], value='tab-3')

                     ]),
            html.Br(),
        ]
    ), id="tabs-collapse", is_open=False)
