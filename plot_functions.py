# READ DATA FROM CSV FILES IN StockOptions directory 
path = '../StockOptions/data/'
import pandas as pd 
import numpy as np 
import datetime as dt
from glob import glob
from tqdm import tqdm
from datafunctions import *
from scipy import stats, signal
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def get_volume_profile(symbol, sp, start_date=None, end_date=None):
    if start_date is None:
        data = add_stock_price(symbol, sp).drop('Adj Close', axis=1).copy()
    else: 
        data = add_stock_price(symbol, sp)[start_date:end_date].drop('Adj Close', axis=1).copy()

    # get stock data 
    kde_factor = .10
    num_samples = 500 
    xr = np.linspace(data['Close'].min(), data['Close'].max(), num_samples)
    kde = stats.gaussian_kde(data['Close'],weights=data['Volume'],bw_method=kde_factor)
    kdy = kde(xr)
    ticks_per_sample = (xr.max()-xr.min())/num_samples
    
    kx = np.linspace(data['Close'].min(), data['Close'].max(),num_samples)
    ky = kde(xr)
    min_prom = ky.max() *.3

    # Calculate Average Trading Range 
    high_low = data['High'] - data['Low']
    high_close = np.abs(data['High'] - data['Close'].shift())
    low_close = np.abs(data['Low'] - data['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    atr = true_range.rolling(14).sum()/14
    max_width_pips = atr.mean()
    
    min_prom = kdy.max() * 0.3
    width_range=(.01, max_width_pips*.0001 / ticks_per_sample)
    peaks, peak_props = signal.find_peaks(kdy, width=0, prominence=min_prom)
    
    
    pkx = xr[peaks]
    pky = kdy[peaks]
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(name='VolumeProfiler', x=data['Close'], y=data['Volume'], nbinsx= 150, opacity=0.6,histfunc='sum',histnorm='probability density'))
    fig.add_trace(go.Scatter(name='KDE', x=xr, y=kdy, mode='lines'))
    fig.add_trace(go.Scatter(name= 'Peaks', x = pkx, y= pky, mode='markers'))


    left_base = peak_props['left_bases']
    right_base = peak_props['right_bases']
    line_x = pkx
    line_y0 = pky
    line_y1 = pky- peak_props['prominences']

    left_ips = peak_props['left_ips']
    right_ips = peak_props['right_ips']
    width_x0 = xr.min() + (left_ips * ticks_per_sample)
    width_x1 = xr.min() + (right_ips * ticks_per_sample)
    width_y = peak_props['width_heights']

    for x,y0,y1 in zip(line_x, line_y0, line_y1):
        fig.add_shape(type='line',xref='x',yref='y',x0=x, y0=y0, x1=x, y1=y1,line=dict(color='black',width=2,))
    
    for x0, x1, y in zip(width_x0, width_x1, width_y):
        fig.add_shape(type='line',xref='x', yref='y',x0=x0, y0=y, x1=x1, y1=y,line=dict(color='black',width=2,))

    return fig


def dual_plot(dropdown_value, sp):
    df = add_stock_price(dropdown_value, sp)
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(x=df.index, y=df.High, name="yaxis data"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=df.index, y=df.Low.pct_change(), name="yaxis2 data"),
        secondary_y=True,
    )

    # Add figure title
    fig.update_layout(
        title_text=f'{dropdown_value} Close Price'
    )

    # Set x-axis title
    fig.update_xaxes(title_text="<b>Date</b>")

    # Set y-axes titles
    fig.update_yaxes(title_text="<b>Stock Price</b>", secondary_y=False)
    fig.update_yaxes(title_text="<b>Volume</b>", secondary_y=True)
    
    return fig