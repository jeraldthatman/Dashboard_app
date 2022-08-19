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
from datafunctions import *

stocks = ['spy', 'aapl', 'tlt', 'qqq']
lod = {i: load_data(i, 100) for i in stocks}
sp = get_price_data(stocks)
stock_names = [{'label': f'{val.upper()}','value': val} for val in stocks]

app = dash.Dash(external_stylesheets=[dbc.themes.CYBORG])

app.layout = html.Div(id = 'parent', children = [ 
    html.H1(id = 'H1', children = 'Stock Dashboard', style = {'textAlign':'center','marginTop':40,'marginBottom':40}),
    # Create Dropdown of stock names
    dcc.Dropdown( id = 'dropdown', options = stock_names, value = 'SPY'),
    dcc.Graph(id = 'OpenInterest')
    ])

@app.callback(Output(component_id='OpenInterest', component_property= 'figure'), [Input(component_id='dropdown', component_property= 'value')])
def graph_update(dropdown_value):
    # Create a bubble chart of Open Interest with a slider to change the expiration date. 
    # Bubble Plot 
    def bubble_plot(stock):
        df = lod[stock].copy().reset_index().dropna()
        df['Expiration'] = df['expiry'].dt.strftime('%Y-%m-%d').astype(str)
        fig = px.scatter(data_frame=df, x="strike", y='openInterest', animation_frame = 'Expiration', animation_group = 'openInterest',
                size = 'openInterest', color = "type", hover_name = "strike",
                hover_data = ["strike", "openInterest"])
        fig.update_layout(title=f'${stock.upper()}', xaxis_title='Strike Price', yaxis_title='Open Interest')
        fig["layout"].pop("updatemenus")
        return fig
    return bubble_plot(dropdown_value)


if __name__ == '__main__': 
    app.run_server()
    