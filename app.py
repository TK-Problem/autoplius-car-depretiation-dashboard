# packages for dash app
from dash import Dash, no_update
from dash.dependencies import Input, Output, State
# plotting libraries
# import plotly.express as px
import plotly.graph_objects as go
# Data processing
# import pandas as pd
import numpy as np
# custom helper functions
from utils import reduce_mem_usage, get_data_graph_left, my_template, get_data_graph_right
# html layouts
from layouts import *

# read .csv from dropbox link.
df_png = pd.read_csv('https://www.dropbox.com/s/i9vzubdk5klhw5q/png_database.csv?dl=1')
# generate car id dictionary for dropdown menu
car_name_dict = [{'label': _, 'value': _} for _ in df_png.Car.unique()]
# reset index for simpler data accessing
df_png.set_index(['Car', 'Year_made'], inplace=True)
# download devaluation data
df_dev = pd.read_csv('https://www.dropbox.com/s/81pxbt3sila32ao/0_all_deval_prices.csv?dl=1')
# reduce memory usage for better performance
df_dev = reduce_mem_usage(df_dev)


app = Dash(__name__,
           meta_tags=[{"name": "viewport", "content": "width=device-width"}],
           suppress_callback_exceptions=True)
server = app.server


app.layout = html.Div(
    [
        header,
        dbc.Container(
            [
                html.Div(
                    [
                        dcc.Dropdown(
                            id='car-name-drop-menu',
                            options=car_name_dict,
                            value='car-name',
                            clearable=False,
                            placeholder="Pasirinkite automobilio modelį"
                        ),
                        html.Br(),
                        tabs_layout
                    ]
                )
            ]
        ),
        footer
    ]
)


@app.callback(
    [Output(component_id='car-year-drop-menu', component_property='options'),
     Output(component_id='car-year-drop-menu', component_property='value'),
     Output(component_id='tabs-collapse', component_property='is_open')],
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
    [Output("png-collapse", "is_open"),
     Output("image-collapse-button", "children")],
    [Input("image-collapse-button", "n_clicks")],
    [State("png-collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        if is_open:
            return not is_open, 'Rodyti originalų autoplius grafiką'
        else:
            return not is_open, 'Slėpti originalų autoplius grafiką'
    return is_open, no_update


@app.callback(
    [Output(component_id='deval-auto-plius-img', component_property='src'),
     Output(component_id="deval-chart-description", component_property='children')],
    [Input(component_id='car-name-drop-menu', component_property='value'),
     Input(component_id='car-year-drop-menu', component_property='value')])
def autoplius_png(car_name, year_made):
    global df_png
    # generate message for graph
    msg = f"Lyginamosios kainos {year_made} metais pagamintų {car_name} automobilių kainos ir jų " \
          f"kitimas, neatsižvelgiant į automobilių komlektaciją ir būklę. "

    # no changes are made if default dropdown menu values are provided
    if year_made == 'year' or car_name == 'car-name':
        return no_update
    else:
        return [df_png.loc[(car_name, int(year_made))].png_url, msg]


@app.callback(
    Output("tab-1-deval-chart", "figure"),
    [Input(component_id='car-name-drop-menu', component_property='value'),
     Input(component_id='car-year-drop-menu', component_property='value')])
def update_tab_1_chart(car_name, year_made):
    global df_dev
    # no changes are made if default dropdown menu values are provided
    if year_made == 'year' or car_name == 'car-name':
        return no_update

    # generate data for left graph
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
    [Output("tab-2-deval-chart", "figure"),
     Output("tab-2-chart-fig-des", "children")],
    [Input(component_id='car-name-drop-menu',
           component_property='value')])
def update_tab_2_chart(car_name):
    global df_dev
    if car_name == 'car-name':
        return no_update
    # select specific data
    df_plot, price_median = get_data_graph_right(df_dev, car_name)

    # create figure with min, max and avg. price changes
    fig = px.line(df_plot, x="Year_diff", y="PCT_change",
                  color='Range', hover_data=['Hover_msg'],
                  labels={'PCT_change': 'Metinis kainos pokytis (%)', 'Year_diff': 'Metų skaičius nuo pagaminimo'})

    # update hovering
    fig.update_traces(mode="markers", hovertemplate='%{customdata[0]}')

    # car model
    # car_model = ' '.join(car_name.split()[1:])

    # add median yearly price change
    fig.add_trace(go.Scatter(x=price_median.index, y=price_median, name=f'Metinio {car_name} kainos pokyčio mediana',
                             marker=dict(size=10), line=dict(color='firebrick', width=4, shape='spline'),
                             hovertemplate='%{y:.1f}%'))

    # update axis values
    fig.update_xaxes(tickvals=np.arange(price_median.index.min(), price_median.index.max() + 1))
    # limit y- axis range if outliers are present
    if price_median.max() * 5 < df_plot.PCT_change.max() or price_median.min() * 5 > df_plot.PCT_change.min():
        fig.update_yaxes(range=[df_plot.PCT_change.quantile(0.05), df_plot.PCT_change.quantile(0.95)])

    fig.update_layout(legend_title_text='',
                      template=my_template,
                      legend=dict(orientation="h", yanchor="top", y=1.1, xanchor="center", x=0.5, font_size=14))
    txt = f"Šią tendenciją palyginame su visų {car_name.split()[0]} pagamintų automobilių " \
          f"ir visų automobilių vidutine kainos kitimo tendencijomis. "
    return fig, txt


if __name__ == '__main__':
    app.run_server(debug=True)
