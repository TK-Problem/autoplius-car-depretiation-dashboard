# packages for dash app
from dash import Dash, dcc, html, no_update
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
# plotting libraries
import plotly.express as px
import plotly.graph_objects as go
# Data processing
import pandas as pd
import numpy as np
# custom helper functions
from utils import reduce_mem_usage, get_data_graph_left, my_template, get_data_graph_right


# read .csv from dropbox link.
df_png = pd.read_csv('https://www.dropbox.com/s/9yahgizebzqwdhn/png_database.csv?dl=1')
# generate car id dictionary for dropdown menu
car_name_dict = [{'label': _, 'value': _} for _ in df_png.Car.unique()]
# reset index for simpler data accessing
df_png.set_index(['Car', 'Year_made'], inplace=True)
# download devaluation data
df_dev = pd.read_csv('https://www.dropbox.com/s/06dpd184dig2jcp/0_all_deval_prices.csv?dl=1')
# reduce memory usage for better performance
df_dev = reduce_mem_usage(df_dev)


app = Dash(__name__,
           meta_tags=[{"name": "viewport", "content": "width=device-width"}],
           suppress_callback_exceptions=True)
server = app.server

tab1_content = dbc.Card(
                dbc.CardBody(
                    [
                        html.H4("Pagaminimo metai", className="card-title"),
                        dcc.Dropdown(id='car-year-drop-menu', options=[], value='year', clearable=False,
                                     placeholder="Pasirinkite mašinos pagaminimo metus"),
                        html.Hr(),
                        dcc.Graph(id="left-deval-chart", config={'displayModeBar': False, 'responsive': False}),
                        html.Img(id='deval-auto-plius-img', src='', style={'width': '100%'}),
                    ]
                ),
                className="mt-3",
)

tab2_content = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Kainos metiniai pokyčiai", className="card-title"),
            dcc.Graph(id="right-deval-chart", config={'displayModeBar': False, 'responsive': False}),
        ]
    ),
    className="mt-3",
)

app.layout = dbc.Container([
    html.Div([
        html.H4('Automobilio modelio pasirinkimas'),
        dcc.Dropdown(
            id='car-name-drop-menu',
            options=car_name_dict,
            value='car-name',
            clearable=False,
            placeholder="Pasirinkite automobilio modelį"
        ),
        dbc.Fade(
                dbc.Tabs(
                    [
                        dbc.Tab(tab1_content, label="Kainų kitimas", className="nav nav-tabs"),
                        dbc.Tab(tab2_content, label="Kainų kitimo dinamika", className="nav nav-tabs"),
                    ]
                ),
                id="tabs-fade",
                is_in=False,
                appear=False,
        ),
    ])
])


@app.callback(
    [Output(component_id='car-year-drop-menu', component_property='options'),
     Output(component_id='car-year-drop-menu', component_property='value'),
     Output(component_id='tabs-fade', component_property='is_in')],
    [Input(component_id='car-name-drop-menu', component_property='value')])
def update_year_made(car_name):
    """
    Updates drop down list with years car was made.
    Dropdown menu value is set to oldest car made.
    Input:
        car_name, str
    Return:
        dict, years that car was made
    """
    global df_png
    # don't update during initial launch
    if car_name == 'car-name':
        return no_update
    # get only unique values for specific car years
    years = df_png.loc[car_name].index
    years = [{'label': year, 'value': year} for year in years]
    # update with oldest available years
    return years, years[0]['value'], True


@app.callback(
    [Output(component_id='deval-auto-plius-img', component_property='src')],
    [Input(component_id='car-name-drop-menu', component_property='value'),
     Input(component_id='car-year-drop-menu', component_property='value')])
def autoplius_png(car_name, year_made):
    global df_png
    # no changes are made if default dropdown menu values are provided
    if year_made == 'year' or car_name == 'car-name':
        return no_update
    else:
        return [df_png.loc[(car_name, int(year_made))].png_url]


@app.callback(
    Output("left-deval-chart", "figure"),
    [Input(component_id='car-name-drop-menu', component_property='value'),
     Input(component_id='car-year-drop-menu', component_property='value')])
def update_left_chart(car_name, year_made):
    global df_dev
    # no changes are made if default dropdown menu values are provided
    if year_made == 'year' or car_name == 'car-name':
        return no_update
    df_plot = get_data_graph_left(df_dev, car_name, year_made)

    # create figure object
    fig = px.line(df_plot, x="Year", y="Price", color='Range', hover_data=['Msg', 'Range'],
                  labels={'Price': 'Kaina (€)', 'Year': 'Metai'})
    # change tick range
    fig.update_yaxes(tickformat='000')
    # update hovering
    fig.update_traces(mode="markers+lines",
                      hovertemplate='%{customdata[1]}: <b>%{y}€</b><br>%{customdata[0]}')
    # update legend location
    fig.update_layout(legend_title_text='',
                      hovermode="x unified",
                      template=my_template,
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font_size=14))
    return fig


@app.callback(
    Output("right-deval-chart", "figure"),
    [Input(component_id='car-name-drop-menu', component_property='value')])
def update_right_chart(car_name):
    global df_dev
    if car_name == 'car-name':
        return no_update
    # select spesific data
    df_plot, price_median = get_data_graph_right(df_dev, car_name)

    # create figure with min, max and avg. price changes
    fig = px.line(df_plot, x="Year_diff", y="PCT_change",
                  color='Range', hover_data=['Hover_msg'],
                  labels={'PCT_change': 'Metinis kainos pokytis (%)', 'Year_diff': 'Metų skaičius nuo pagaminimo'})

    # update hovering
    fig.update_traces(mode="markers", hovertemplate='%{customdata[0]}')

    # add median yearly price change
    fig.add_trace(go.Scatter(x=price_median.index, y=price_median, name='Metinio kainos pokytčio mediana',
                             marker=dict(size=10), line=dict(color='firebrick', width=4), line_shape='spline',
                             hovertemplate='%{y:.1f}%'))

    # update axis values
    fig.update_xaxes(tickvals=np.arange(price_median.index.min(), price_median.index.max() + 1))
    # limit y- axis range if outliers are present
    if price_median.max() * 3 < df_plot.PCT_change.max() or price_median.min() * 3 > df_plot.PCT_change.min():
        fig.update_yaxes(range=[df_plot.PCT_change.quantile(0.05), df_plot.PCT_change.quantile(0.95)])

    fig.update_layout(legend_title_text='',
                      template=my_template,
                      legend=dict(orientation="h", yanchor="top", y=1.05, xanchor="center", x=0.5, font_size=14))

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
