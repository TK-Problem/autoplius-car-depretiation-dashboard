from dash import Dash, dcc, html, no_update
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from utils import reduce_mem_usage, get_data, my_template

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


app.layout = html.Div([
    html.H4('Car selection'),
    dcc.Dropdown(
        id='car-name-drop-menu',
        options=car_name_dict,
        value='car-name',
        clearable=False,
        placeholder="Select car"
    ),
    html.H4('Year'),
    dcc.Dropdown(
        id='car-year-drop-menu',
        options=[],
        value='year',
        clearable=False,
        placeholder="Select the year car was made"
    ),
    html.Hr(),
    dcc.Graph(id="deval-chart",
              config={'displayModeBar': False, 'responsive': False}),
    html.Hr(),
    html.Img(id='deval-auto-plius-img', src='', style={'width': '100%'}),
])


@app.callback(
    [Output(component_id='car-year-drop-menu', component_property='options'),
     Output(component_id='car-year-drop-menu', component_property='value')],
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
    return years, years[0]['value']


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
    Output("deval-chart", "figure"),
    [Input(component_id='car-name-drop-menu', component_property='value'),
     Input(component_id='car-year-drop-menu', component_property='value')])
def update_line_chart(car_name, year_made):
    global df_dev
    # no changes are made if default dropdown menu values are provided
    if year_made == 'year' or car_name == 'car-name':
        return no_update
    df_plot = get_data(df_dev, car_name, year_made)

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
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=0.57, font_size=14))
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
