import pandas as pd
import numpy as np
import plotly.io as pio


# modify generic template
my_template = pio.templates["plotly"]
my_template.layout['colorway'] = ('#7fdffa', '#4c93c5', '#60ade1')
my_template.layout['plot_bgcolor'] = 'rgba(0,0,0,0)'
my_template.layout['yaxis']['gridcolor'] = 'rgba(1,1,1,0.3)'
my_template.layout['xaxis']['gridcolor'] = 'rgba(1,1,1,0.3)'


# reduce memory usage if available
def reduce_mem_usage(df, verbose=False):
    """
    Change pandas dtypes to reduce memory usage
    Input:
        df, pandas DataFrame
        verbose, bool, if True print message
    Output:
        pandas DataFrame
    """
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    start_mem = df.memory_usage().sum() / 1024**2
    for col in df.columns:
        col_type = df[col].dtypes
        if col_type in numerics:
            c_min = df[col].min()
            c_max = df[col].max()
            if str(col_type)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int64)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)
            else:
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float32)
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float64)
                else:
                    df[col] = df[col].astype(np.float64)
    end_mem = df.memory_usage().sum() / 1024**2
    if verbose:
        # reduced memory usage in percent
        diff_pst = 100 * (start_mem - end_mem) / start_mem
        msg = f'Mem. usage decreased to {end_mem:5.2f} Mb ({diff_pst:.1f}% reduction)'
        print(msg)
    return df


def get_data_tab_1_graph(df, car_name, year_made):
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

    def format_msg(row, min_year):
        """
        Helper function to generate hover message.
        Input:
            row, pandas Series
            min_year, int
        Output:
            str, message for hovering
        """
        if row['Year'] == min_year:
            return f"<extra></extra>"
        else:
            if row['Change'] > 0:
                return f"Pakilo {row['Change'] * 100:.1f}%." + '<extra></extra>'
            elif row['Change'] < 0:
                return f"Nukrito {row['Change'] * 100:.1f}%." + '<extra></extra>'
            else:
                return f"Kaina {row['Price']}€ nepakito." + '<extra></extra>'

    # calculate pct price change
    df_plot['Change'] = df_plot.Price / df_plot.Price.shift(1) - 1
    # create new column with message for hovering
    df_plot['Msg'] = df_plot.apply(lambda x: format_msg(x, df_plot.Year.min()), axis=1)

    return df_plot


def get_data_tab_2_graph(df, car_name):
    """
    Transforms pandas DataFrame for plotling prices.
    Calculates median price change
    Input:
        df, pandas DataFrame
        car_name, str, car name, e.g. 'Volkswagen Golf Sportsvan'
    Output:
        pandas DataFrame
    """
    # select data only for chosen car name
    df_plot = df.loc[df.Car == car_name].copy()
    # calculate how many years passed
    df_plot['Year_diff'] = df_plot['Year'] - df_plot['Year_made']
    # reshape DataFrame
    df_plot = pd.melt(df_plot[['Year_made', 'Car', 'Low', 'Medium', 'High', 'Year_diff']],
                      id_vars=['Year_made', 'Car', 'Year_diff'], var_name='Range', value_name='Price')

    # rename price ranges to lithuanian
    df_plot.Range = df_plot.Range.replace({'Low': 'Mažiausios kainos pokyčiai',
                                           'Medium': 'Vidutinės kainos pokyčiai',
                                           'High': 'Didžiausios kainos pokyčiai'})

    # calculate percentage price changes
    df_plot['PCT_change'] = (df_plot['Price'] / df_plot['Price'].shift(1) - 1) * 100
    # remove prices from same year
    df_plot = df_plot.loc[df_plot.Year_diff != 0].copy()
    # calculate avg price change
    price_median = df_plot.groupby('Year_diff')['PCT_change'].median()

    def gen_hover_txt(row):
        """
        Generate hover message
        """
        msg = f"<b>{row['Year_made']}</b> metais pagaminto <br>"
        # generate new word based on range
        d = {'Mažiausios kainos pokyčiai': 'mažiausia kaina',
             'Vidutinės kainos pokyčiai': 'vidutinė kaina',
             'Didžiausios kainos pokyčiai': 'didžiausia kaina'}

        msg += f"{row['Car']}<br>{d[row['Range']]} <br>"
        if row['PCT_change'] < 0:
            msg += f"per metus nukrito {row['PCT_change']:.1f}%."
        elif row['PCT_change'] > 0:
            msg += f"per metus pakilo {row['PCT_change']:.1f}%."
        else:
            msg += f'per metus nepakito.'

        # remove y-axis label from appearing during hover
        return msg + '<extra></extra>'

    # generate hover message
    df_plot['Hover_msg'] = df_plot.apply(gen_hover_txt, axis=1)

    return df_plot, price_median
