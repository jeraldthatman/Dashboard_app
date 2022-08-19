import dash
from dash import html as html 
from dash import dcc as dcc
from dash.dependencies import Input, Output  
import plotly.express as px
from datafunctions import * 
from plot_functions import *
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from names import Stock_names
#lod = {i: load_data(i, 100) for i in STOCKS}


# Basic Stock Dashboard
app = dash.Dash(external_stylesheets=[dbc.themes.CYBORG])

sp = get_price_data(STOCKS)

from names import Stock_names 

app.layout = html.Div(id = 'parent', children = [
    html.H1(id = 'H1', children = 'Stock Dashboard', style = {'textAlign':'center',\
                                            'marginTop':40,'marginBottom':40}),
        dcc.Dropdown( id = 'dropdown',
        options = [{'label': f'{val} ({key})', 'value': key} for key, val in Stock_names.items()],
        value = 'SPY'),
        dcc.Graph(id = 'bar_plot'),
        dcc.Graph(id = 'VolumeProfile'), 
        dcc.Graph(id = 'Stock Returns')
    ])
    
    
@app.callback(Output(component_id='bar_plot', component_property= 'figure'),
              [Input(component_id='dropdown', component_property= 'value')])
    
def graph_update(dropdown_value):
    def candle_stick(stock):
        df = add_stock_price(stock, sp)
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close))
        fig.update_layout(xaxis_rangeslider_visible=False)
        fig.update_layout(title_text=f'${stock.upper()} Stock Price')
        fig.update_xaxes(title_text="<b>Date</b>")
        fig.update_yaxes(title_text="<b>Price</b>")
        return fig
    return candle_stick(dropdown_value)

@app.callback(Output(component_id='VolumeProfile', component_property= 'figure'),
                [Input(component_id='dropdown', component_property= 'value')])

def volume_profiler(dropdown_value):
    fig = get_volume_profile(dropdown_value, sp, '2021-01-01', '2022-08-09')
    fig.update_layout(title = f'${dropdown_value.upper()} Volume Profile',
                      xaxis_title = 'Volume in Millions',
                      yaxis_title = 'Profile'
                      )
    return fig

@app.callback(Output(component_id='Stock Returns', component_property= 'figure'),
                [Input(component_id='dropdown', component_property= 'value')])

def stock_returns(dropdown_value):
    def Stock_returns(stock):
        df = add_stock_price(stock, sp)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df.Close.pct_change(), name="Returns"))
        fig.update_layout(title_text=f'{stock} Returns')
        fig.update_xaxes(title_text="<b>Date</b>")
        fig.update_yaxes(title_text="<b>Returns</b>")
        return fig
    return Stock_returns(dropdown_value)

if __name__ == '__main__': 
    app.run_server()
    