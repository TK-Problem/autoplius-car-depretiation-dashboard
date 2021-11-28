from dash import Dash, dcc, html, no_update
from dash.dependencies import Input, Output
import pandas as pd

# read .csv from dropbox link.
df_png = pd.read_csv('https://www.dropbox.com/s/b4nxy7zozz7fqtq/png_database.csv?dl=1')
# generate car id dictionary for dropdown menu
car_name_dict = [{'label': _, 'value': _} for _ in df_png.Car.unique()]
# reset index for simpler data accessing
df_png.set_index(['Car', 'Year_made'], inplace=True)


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
    html.Img(id='deval-auto-plius-img', src=''),
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
    if year_made == 'year' or car_name == 'car-name':
        return no_update
    else:
        return [df_png.loc[(car_name, int(year_made))].png_url]


if __name__ == '__main__':
    app.run_server(debug=True)
