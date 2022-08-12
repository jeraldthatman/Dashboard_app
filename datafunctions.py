import pandas as pd 
import numpy as np 
import datetime as dt
from glob import glob
import yfinance as yf

path = '../StockOptions/data/'

STOCKS = [str(x).split('/')[3] for x in glob('../StockOptions/data/*')]


def group_multi_index(option_df):
    """Groups the multi index of the dataframe and calculate Volume Percent Changes etc."""
    df = option_df.sort_values(['contractSymbol', 'gatherDate']).copy()
    df = df.set_index(['contractSymbol', 'gatherDate'])
    df['volume_pctChange'] = df['volume'].pct_change().round(2)
    df['oi_pctChange'] = df['openInterest'].pct_change().round(2)
    df['price_pctChange'] = df['lastPrice'].pct_change().round(2) 
    return df

def cast0(df, key, value, join_how='outer'):
    from pandas import DataFrame
    """Casts the input data frame into a tibble,
    given the key column and value column.
    """
    assert type(df) is DataFrame
    assert key in df.columns and value in df.columns
    assert join_how in ['outer', 'inner']
    
    fixed_vars = df.columns.difference([key, value])
    tibble = DataFrame(columns=fixed_vars) # empty frame
    
    ### BEGIN SOLUTION
    new_vars = df[key].unique()
    for v in new_vars:
        df_v = df[df[key] == v]
        del df_v[key]
        df_v = df_v.rename(columns={value: v})
        tibble = tibble.merge(df_v,
                            on=list(fixed_vars),
                            how=join_how)
    ### END SOLUTION
    return tibble

def load_data(symbol, n = 30, include_expired = False, today = False):
    """Gets the last n TRADING days data and returns the concatenated data frame'"""
    fnames = sorted(glob(path+ f'{symbol}/OptionChain*'), reverse=False)
    if n> len(fnames):
        fnames = fnames
    else: 
        fnames = [fnames[-i] for i in range(1, (n+1))]

    dframes = []
    for i in fnames: 
        """ Appends the daily dataframes for each day. """
        #scrapes the date from the file name
        date_recorded = str(i).split('_')[-1].split('.')[0]
        df =pd.read_csv(i) 
        if len(df) > 10:
            del df['cash']

            del df['vol/oi']
            if 'gatherDate' not in df:
                df.insert(0, 'gatherDate', date_recorded)
            df.insert(0, 'stock', symbol)
            #df['dayToExp'] = np.datetime64(df['expiry']) - df.gatherDate
            df['timeValue'] = (pd.to_datetime(df['expiry']) - pd.to_datetime(df['gatherDate']))/ np.timedelta64(1,'D')/252
            #df['percentChange'] = df['percentChange']/100
            from datetime import datetime as dt 
            if include_expired == False:
                df = df[df['expiry']>= dt.today().strftime('%Y-%m-%d')]
                dframes.append(df)
            if include_expired == True:
                dframes.append(df)
    # Concatenate the dataframes  
    out = pd.concat([df for df in dframes])
    out = out.loc[:,~out.columns.str.startswith('U')]
    out['gatherDate']  = pd.to_datetime(out['gatherDate'])
    out['expiry'] = pd.to_datetime(out['expiry'])
    out = group_multi_index(out)
    
    if today == False:
        return out
    else: 
        out = out.reset_index()
        return out[out['gatherDate'] == out['gatherDate'].max()]

def get_price_data(stocks, download = False):
    """ Get price data for stocks """
    if download != False: 
        stock_price = yf.download(stocks, start='2013-01-01')
        stock_price.columns.names =['Metric', 'Stock_name']
        stock_price.head()
        stock_price.to_csv('stock_prices.csv')
        return stock_price
    else: 
        sp = pd.read_csv('stock_prices.csv', header=[0,1])
        sp.set_index(sp.columns[0], inplace= True)
        sp.index.name = 'Date'
        sp.columns.names =['Metric', 'Stock_name']
        return  sp.iloc[1:, :]

# get ohlcv for a prticular symbol 
def add_stock_price(stock, sp):
    """Slice dataframe to get stock price for a particular symbol"""
    out = sp.xs(key = stock.upper(), axis = 1, level = 'Stock_name', drop_level=True)
    out.columns.names = ['']
    out.columns = out.columns.get_level_values(0)
    return out
