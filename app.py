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



app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

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
        dcc.Graph(id = 'Dual_plot')
    ])
    
    
@app.callback(Output(component_id='bar_plot', component_property= 'figure'),
              [Input(component_id='dropdown', component_property= 'value')])
    
def graph_update(dropdown_value):
    print(dropdown_value, '\n')
    df = add_stock_price(dropdown_value, sp)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x = df.index, y = df['Close']))
    fig.update_layout(title = f'{dropdown_value} Close Price', xaxis_title = 'Date', yaxis_title = 'Price')
    # Ret
    return fig  

@app.callback(Output(component_id='VolumeProfile', component_property= 'figure'),
                [Input(component_id='dropdown', component_property= 'value')])

def volume_profiler(dropdown_value):
    fig = get_volume_profile(dropdown_value, sp, '2021-01-01', '2022-08-09')
    fig.update_layout(title = f'${dropdown_value.upper()} Volume Profile',
                      xaxis_title = 'Volume in Millions',
                      yaxis_title = 'Profile'
                      )
    return fig


@app.callback(Output(component_id='Dual_Plot', component_property= 'figure'),
              [Input(component_id='dropdown', component_property= 'value')])

def dual_plot_space(dropdown_value):
    return dual_plot(dropdown_value, sp)


if __name__ == '__main__': 
    app.run_server()
    