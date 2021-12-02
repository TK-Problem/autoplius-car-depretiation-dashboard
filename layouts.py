from dash import dcc, html
import dash_bootstrap_components as dbc


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
                html.Div("t.uzdavinys@gmail.com", style={'textAlign': 'center'})
            ],
            width={"size": 6, "offset": 3},

        ),
    ),
    className='card text-white bg-dark mb-3'
)


tab1_content = dbc.Card(
                dbc.CardBody(
                    [
                        html.H4("Pagaminimo metai", className="card-title"),
                        dcc.Dropdown(id='car-year-drop-menu', options=[], value='year', clearable=False,
                                     placeholder="Pasirinkite mašinos pagaminimo metus"),
                        html.Br(),
                        html.P('', id="deval-chart-description", className="tab-text"),
                        dcc.Graph(id="left-deval-chart", config={'displayModeBar': False, 'responsive': False}),
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
            html.P("Modelio aprašymas.", className="card-text"),
            dcc.Graph(id="right-deval-chart", config={'displayModeBar': False, 'responsive': False}),
        ]
    ),
    className="mt-3",
)


tab3_content = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Modelis", className="card-title"),
            html.P("Laikinas tekstas (PLACEHOLDER)", className="card-text")
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
                         dcc.Tab(label='Kainų kitimo dinamika', children=[tab2_content], value='tab-2'),
                         dcc.Tab(label='Kainos nuvertėjimo modelis', children=[tab3_content], value='tab-3')

                                ]),
            html.Br(),
          ]
    ), id="tabs-collapse", is_open=False)
