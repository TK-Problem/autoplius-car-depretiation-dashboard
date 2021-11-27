from dash import Dash, dcc, html, no_update
from dash.dependencies import Input, Output
import pandas as pd

# read datata from dropbox link
df = pd.read_csv('https://www.dropbox.com/s/yxrjr9fai5zub3c/2011_cars_test.csv?dl=1', index_col=0)

# generate car id dictionary for dropdown menu
car_name_dict = [{'label': _, 'value': _} for _ in df.Car.unique()]


app = Dash(__name__,
           meta_tags=[{"name": "viewport", "content": "width=device-width"}],
           suppress_callback_exceptions=True)
server = app.server


app.layout = html.Div([
    html.H4('Car selection- placeholder'),
    dcc.Dropdown(
        id='car-name-drop-menu',
        options=car_name_dict,
        value='car-name',
        clearable=False,
        placeholder="Select car"
    ),
    html.H4('Year made- placeholder'),
    dcc.Dropdown(
        id='car-year-drop-menu',
        options=[],
        value='year',
        clearable=False,
        placeholder="Select the year car was made"
    ),
])


@app.callback(
    [Output(component_id='car-year-drop-menu', component_property='options'),
     Output(component_id='car-year-drop-menu', component_property='value')],
    [Input(component_id='car-name-drop-menu', component_property='value')])
def update_year_made(car_name):
    """
    Updates drop down list with years car was made.
    Include only those years for which data/.png files are available
    Input:
        car_name, str
    Return:
        dict, years that car was made
    """
    global df
    # don't update during initial launch
    if car_name == 'car-name':
        return no_update
    # get only unique values for specific car years
    years = df.loc[df.Car == car_name, 'Year_made'].unique()
    years = [{'label': year, 'value': year} for year in years]
    # update with earliest available years
    return years, years[0]['value']


if __name__ == '__main__':
    app.run_server(debug=True)
