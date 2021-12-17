# packages for dash app
from dash import Dash, no_update
from dash.dependencies import Input, Output, State
# plotting libraries
import plotly.graph_objects as go
# Data processing
import numpy as np
# custom helper functions
import utils
# html layouts
from layouts import *

# read .csv from dropbox link.
DF_PNG = pd.read_csv('https://www.dropbox.com/s/i9vzubdk5klhw5q/png_database.csv?dl=1')
# generate car id dictionary for dropdown menu
car_name_dict = [{'label': _, 'value': _} for _ in DF_PNG.Car.unique()]
# reset index for simpler data accessing
DF_PNG.set_index(['Car', 'Year_made'], inplace=True)
# download devaluation data
DF_DEV = pd.read_csv('https://www.dropbox.com/s/g7u36zpj7i4hlxp/0_all_deval_prices_4.csv?dl=1')
# reduce memory usage for better performance
DF_DEV = utils.reduce_mem_usage(DF_DEV)
# transform DataFrame for plotting, calculate yearly changes
DF_YEARLY = utils.calculate_yearly_changes(DF_DEV)
# calculate median yearly price change
YEARLY_MEDIAN = DF_YEARLY.groupby('Year_diff')['PCT_change'].median()
# create global DataFrames for plotting
DF_TAB_2_MODEL = pd.DataFrame()
DF_TAB_2_MODEL_MEDIAN = pd.DataFrame()
DF_TAB_2_MANU = pd.DataFrame()
DF_TAB_2_MANU_MEDIAN = pd.DataFrame()

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
    [Output('car-year-drop-menu', 'options'),
     Output('tab-2-year-select', 'options'),
     Output('car-year-drop-menu', 'value'),
     Output('tab-2-year-select', 'value'),
     Output('tabs-collapse', 'is_open')],
    [Input('car-name-drop-menu', 'value')])
def update_year_made(car_name):
    """
    Updates drop down list with years car was made.
    Dropdown menu value is set to oldest car made.
    Input:
        car_name, str
        is_open, bool
    Return:
        dict, list, years that car was made, e.g. [{'label': 2009, 'value': 2009}, {'label': 2010, 'value': 2010}]
    """
    global DF_TAB_2_MODEL, DF_TAB_2_MANU, DF_TAB_2_MODEL_MEDIAN, DF_TAB_2_MANU_MEDIAN
    # don't update during initial launch
    if car_name == 'car-name':
        return no_update

    # get only unique values for specific car years
    years = DF_PNG.loc[car_name].index
    # select only max 10 years old cars for calculating devaluation
    # years_select = [{'label': k, 'value': k} for k in years if k >= 2015]
    # update png drop-down manu list year options
    years = [{'label': year, 'value': year} for year in years]

    # quick but dirty solution to speed-up data loading, store element is not used- global variables instead
    # load specific data for plotting
    DF_TAB_2_MODEL, DF_TAB_2_MANU, DF_TAB_2_MODEL_MEDIAN, DF_TAB_2_MANU_MEDIAN = utils.get_data_tab_2_graph(DF_YEARLY,
                                                                                                            car_name)

    # update dropdown with the oldest available years
    return years, years, years[0]['value'], years[0]['value'], True


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
    [Output("tab-2-calcualte-deval-btn", "disabled")],
    [Input('tab-2-year-select', 'value'), Input('tab-2-price', 'value')]
)
def activate_calculation_btn(year_car_made, car_price):
    if year_car_made is None or car_price is None:
        return [True]

    try:
        # convert to integer
        car_price = int(car_price)
    except:
        # if car price can't be converted to number ignore calculations
        return [True]

    if isinstance(car_price, int):
        return [False]
    return [True]


@app.callback(
    [Output("deval-calculation-results-collapse", "is_open"),
     Output("tab-2-calc-chart", "figure"),
     Output("markdown-text", "children")],
    [Input("tab-2-calcualte-deval-btn", "n_clicks")],
    [State('tab-2-year-select', 'value'), State('tab-2-price', 'value'),
     State("deval-calculation-results-collapse", "is_open")],
)
def toggle_calculation_results(n, year_car_made, car_price, is_open):
    if n:
        # get devaluation years 5 years in the future
        _index = [_ - int(year_car_made) for _ in range(2022, 2027)]
        # get only max range based on available data on all sales
        _index = [_ for _ in _index if _ <= max(YEARLY_MEDIAN.index)]
        # temp. DataFrame for plotting
        _df = pd.DataFrame(index=_index)
        _df['All'] = YEARLY_MEDIAN.loc[_index]
        _df = _df.join(DF_TAB_2_MODEL_MEDIAN).rename(columns={'PCT_change': 'Model'})
        _df = _df.join(DF_TAB_2_MANU_MEDIAN).rename(columns={'PCT_change': 'Manu'})
        _df.loc[0] = [car_price, car_price, car_price]
        # re-sort values
        _df = _df.sort_index()
        # get devaluation pct changes based on model
        for i in range(1, len(_df)):
            _df.iloc[i] = _df.iloc[i - 1].values * (100 + _df.iloc[i].values) / 100

        # add hover messages
        for col_name in ['All', 'Model', 'Manu']:
            _df.loc[_index, f'{col_name}_msg'] = 1 - _df[col_name] / car_price
            _df.loc[_index,
                    f'{col_name}_msg'] = _df.loc[_index,
                                                 f'{col_name}_msg'].apply(lambda x: f', {100 - x * 100:.1f}% vertės')
            _df[f'{col_name}_msg'] = _df[f'{col_name}_msg'].fillna('')

        # _df.loc[_index, 'All_msg'] = 1 - _df['All'] / car_price
        # _df.loc[_index, 'All_msg'] = _df.loc[_index, 'All_msg'].apply(lambda x: f', {100 - x * 100:.1f}% vertės')
        # _df['All_msg'] = _df['All_msg'].fillna('')

        # round values
        _df = _df.round(-2)

        # provide predictions 5 years in the future based on all car devaluation trends
        # prediction based on specific car model devaluation
        fig = go.Figure(data=go.Scatter(x=[_ for _ in range(2021, 2027)],
                                        y=_df.Model, name=f'Modelis #1', text=_df['Model_msg'],
                                        marker=dict(size=10), hovertemplate='%{y}€%{text}',
                                        line=dict(color='firebrick', width=4, shape='spline'))
                        )

        # prediction based on specific car manufacturer devaluation
        fig.add_trace(go.Scatter(x=[_ for _ in range(2021, 2027)], text=_df['Manu_msg'],
                                 y=_df.Manu, name=f'Modelis #2',
                                 marker=dict(size=10), hovertemplate='%{y}€%{text}',
                                 line=dict(color='teal', width=4, shape='spline')))

        # prediction based on all car devaluation
        fig.add_trace(go.Scatter(x=[_ for _ in range(2021, 2027)], text=_df['All_msg'],
                                 y=_df.All, name=f'Modelis #3',
                                 marker=dict(size=10), hovertemplate='%{y}€%{text}',
                                 line=dict(color='GoldenRod', width=4, shape='spline')
                                 ))

        # change tick range
        fig.update_yaxes(tickformat='000')

        # update legend location
        fig.update_layout(legend_title_text='',
                          hovermode="x unified",
                          xaxis_title="Metai",
                          yaxis_title="Kaina (€)",
                          template=utils.my_template,
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font_size=14))

        # get car manufacturer's name
        car_manu = DF_TAB_2_MODEL.Car.values[0].split()[0]

        markdown_text = f"""
        Automobilio kainos kritimas yra įvertintas su 3-im modeliais:
        * modelis #1- metinis kainos nuvertėjimas išskaičiuotas tik iš {DF_TAB_2_MODEL.Car.values[0]}
        * modelis #2- metinis kainos nuvertėjimas išskaičiuotas iš visų {car_manu} gamintojo duomenų,
        * modelis #3- duomenų, metinis kainos nuvertėjimas išskaičiuotas iš visų automobilių duomenų.
        """

        if not is_open:
            return True, fig, markdown_text
        return no_update, fig, markdown_text
    return no_update


@app.callback(
    [Output('price-slider', 'min'),
     Output('price-slider', 'max'),
     Output('price-slider', 'value')],
    Input('tab-2-year-select', 'value'),
    State('car-name-drop-menu', 'value')
)
def update_slider(year_made, car_name):
    # get price range for 2021 year
    prices = DF_DEV.loc[(DF_DEV.Car == car_name) & (DF_DEV.Year_made == int(year_made)) & (DF_DEV.Year == 2021)].copy()
    prices = prices[['Low', 'Medium', 'High']].values
    if len(prices):
        return prices.min(), prices.max(), prices.mean()
    return no_update


@app.callback(
    Output('tab-2-price', 'value'),
    Input('price-slider', 'value'))
def update_price(price):
    # return slider price rounded to hundreds
    return round(int(price), -2)


@app.callback(
    [Output(component_id='deval-auto-plius-img', component_property='src'),
     Output(component_id="deval-chart-description", component_property='children')],
    [Input(component_id='car-name-drop-menu', component_property='value'),
     Input(component_id='car-year-drop-menu', component_property='value')])
def autoplius_png(car_name, year_made):
    # generate message for graph
    msg = f"Lyginamosios kainos {year_made} metais pagamintų {car_name} automobilių kainos ir jų " \
          f"kitimas, neatsižvelgiant į automobilių komlektaciją ir būklę. "

    # no changes are made if default dropdown menu values are provided
    if year_made == 'year' or car_name == 'car-name':
        return no_update
    else:
        return [DF_PNG.loc[(car_name, int(year_made))].png_url, msg]


@app.callback(
    Output("tab-1-deval-chart", "figure"),
    [Input(component_id='car-name-drop-menu', component_property='value'),
     Input(component_id='car-year-drop-menu', component_property='value')])
def update_tab_1_chart(car_name, year_made):
    # no changes are made if default dropdown menu values are provided
    if year_made == 'year' or car_name == 'car-name':
        return no_update

    # generate data for left graph
    df_plot = utils.get_data_tab_1_graph(DF_DEV, car_name, year_made)

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
                      template=utils.my_template,
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font_size=14))
    return fig


@app.callback(
    [Output("tab-2-deval-chart", "figure"),
     Output("tab-2-chart-fig-des", "children")],
    [Input('tabs-collapse', 'is_open'),
     Input('tab-2-radio-items', 'value'),
     Input('tab-2-change-graph-type-btn', 'n_clicks')])
def update_tab_2_charts(tabs_open, radio_value, n):
    # no update during initial app launch
    if not tabs_open:
        return no_update

    # if limited amount of data available don't update
    if not len(DF_TAB_2_MODEL):
        return no_update, 'Permažai duomenų, kad galima būtų įvertinti kainų kitimo tendenciją.'

    # get car name from global DataFrame
    car_name = DF_TAB_2_MODEL.Car.unique()[0]

    if radio_value == 'MODEL':
        df_plot = DF_TAB_2_MODEL
    else:
        # for manufacturer prices select years specific model was sold on autoplius website
        df_plot = DF_TAB_2_MANU.loc[DF_TAB_2_MANU.Year_diff.isin(DF_TAB_2_MODEL.Year_diff.unique())]

    if n % 2 == 0:
        # create figure with min, max and avg. price changes
        fig = px.line(df_plot, x="Year_diff", y="PCT_change",
                      color='Range', hover_data=['Hover_msg'],
                      labels={'PCT_change': 'Metinis kainos pokytis (%)', 'Year_diff': 'Metų skaičius nuo pagaminimo'})
        # update hovering
        fig.update_traces(mode="markers", hovertemplate='%{customdata[0]}')

    else:
        # check if box-plot
        fig = px.box(df_plot, x="Year_diff", y="PCT_change", color='Range', hover_data=['Hover_msg'],
                     labels={'PCT_change': 'Metinis kainos pokytis (%)', 'Year_diff': 'Metų skaičius nuo pagaminimo'})
        # update hovering
        fig.update_traces(hovertemplate='%{customdata[0]}')

    # add median yearly model's price change
    fig.add_trace(go.Scatter(x=DF_TAB_2_MODEL_MEDIAN.index, y=DF_TAB_2_MODEL_MEDIAN,
                             name=f'{car_name} kainos pokyčio mediana',
                             marker=dict(size=10), line=dict(color='firebrick', width=4, shape='spline'),
                             hovertemplate='%{y:.1f}%'))

    # add median yearly manufacturer's price change
    fig.add_trace(go.Scatter(x=DF_TAB_2_MANU_MEDIAN.loc[DF_TAB_2_MODEL_MEDIAN.index].index,
                             y=DF_TAB_2_MANU_MEDIAN.loc[DF_TAB_2_MODEL_MEDIAN.index],
                             name=f'Visų {car_name.split()[0]} modelių kainos pokyčio mediana',
                             marker=dict(size=10), line=dict(color='teal', width=4, shape='spline'),
                             hovertemplate='%{y:.1f}%'))

    # add median yearly all cars and price ranges price change
    fig.add_trace(go.Scatter(x=YEARLY_MEDIAN.loc[DF_TAB_2_MODEL_MEDIAN.index].index,
                             y=YEARLY_MEDIAN.loc[DF_TAB_2_MODEL_MEDIAN.index],
                             name=f'Visų automobilių modelių kainos pokyčio mediana',
                             marker=dict(size=10), line=dict(color='GoldenRod', width=4, shape='spline'),
                             hovertemplate='%{y:.1f}%'))

    # update axis values
    fig.update_xaxes(tickvals=np.arange(DF_TAB_2_MODEL_MEDIAN.index.min(), DF_TAB_2_MODEL_MEDIAN.index.max() + 1))
    # limit y- axis range if outliers are present
    _low = DF_TAB_2_MODEL_MEDIAN.max() * 5 < DF_TAB_2_MODEL.PCT_change.max()
    _high = DF_TAB_2_MODEL_MEDIAN.min() * 5 > DF_TAB_2_MODEL.PCT_change.min()
    if _low or _high:
        fig.update_yaxes(range=[DF_TAB_2_MODEL.PCT_change.quantile(0.05), DF_TAB_2_MODEL.PCT_change.quantile(0.95)])

    # update hover template
    fig.update_layout(legend_title_text='',
                      template=utils.my_template,
                      legend=dict(orientation="h", yanchor="top", y=1.3, xanchor="center", x=0.5, font_size=14))

    txt = f"Šią tendenciją palyginame su visų {car_name.split()[0]} pagamintų automobilių " \
          f"ir visų automobilių vidutine kainos kitimo tendencijomis. "
    return fig, txt


if __name__ == '__main__':
    app.run_server(debug=True)
