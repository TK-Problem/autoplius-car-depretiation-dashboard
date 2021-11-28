from dash import Dash, dcc, html, no_update
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# read .csv from dropbox link.
df_png = pd.read_csv('https://www.dropbox.com/s/9yahgizebzqwdhn/png_database.csv?dl=1')
# generate car id dictionary for dropdown menu
car_name_dict = [{'label': _, 'value': _} for _ in df_png.Car.unique()]
# reset index for simpler data accessing
df_png.set_index(['Car', 'Year_made'], inplace=True)
# download devaluation data
df_dev = pd.read_csv('https://www.dropbox.com/s/06dpd184dig2jcp/0_all_deval_prices.csv?dl=1')


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
    dcc.Graph(id="deval-chart"),
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
                      hovertemplate='<br><b>%{x} metai</b><br>' + '%{customdata[0]}' + '<extra></extra>')
    # update legend location
    fig.update_layout(legend_title_text='',
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=0.57, font_size=14))
    return fig


"""
Helper functions
"""


def get_data(df, car_name, year_made):
    """
    Selects data only for specific  car (car_name variable) made (year_made variable).
    Creates new column with message for hovering with mouse.
    Input:
        df, pandas DataFrame
        car_name, str
        year_made, int
    Output:
        pandas DataFrame
    """
    # select data for car made at specific year
    df_plot = df.loc[(df.Car == car_name) & (df.Year_made == year_made)].copy()
    # reshape DataFrame
    df_plot = pd.melt(df_plot, id_vars=['Year', 'Car', 'Year_made'], var_name='Range', value_name='Price')
    # rename price ranges to lithuanian
    df_plot.Range = df_plot.Range.replace({'Low': 'Mažiausia kaina',
                                           'Medium': 'Vidutinė kaina',
                                           'High': 'Didžiausia kaina'})

    def format_msg(row, min_year=2011):
        """
        Helper function to generate hover message.
        """
        if row['Year'] == min_year:
            return f"{row['Range']} buvo {row['Price']}€."
        else:
            if row['Change'] > 0:
                return f"{row['Range']} {row['Price']}€ Per metus pakilo {row['Change'] * 100:.1f}%."
            elif row['Change'] < 0:
                return f"{row['Range']} {row['Price']}€ Per metus nukrito {row['Change'] * 100:.1f}%."
            else:
                return f"Kaina {row['Price']}€ Per metus nepakito."

    # calculate pct price change
    df_plot['Change'] = df_plot.Price / df_plot.Price.shift(1) - 1
    # create new column with message for hovering
    df_plot['Msg'] = df_plot.apply(lambda x: format_msg(x, df_plot.Year.min()), axis=1)

    return df_plot


if __name__ == '__main__':
    app.run_server(debug=True)
