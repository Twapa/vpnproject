import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.offline as pyo
import plotly.graph_objects as go
from plotly import tools

app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']= True

app.layout = html.Div([
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),

    # content will be rendered in this element
    html.Div(id='page-content'),
    html.Div(id='dummy-div')
])

landing_page = html.Div([
    html.Pre(
            children='Home Page',
        ),
    dcc.Link('Network config', href='/network_config'),
    dcc.Link('LAN config', href='/lan_config'),
])
network_statistics_page = html.Div([
     html.Pre(
            children='network configuration page',
        ),
    dcc.Link('Go to home page', href='/'),
    dcc.Link('Lan config', href='/lan_config'),
])
LAN_configuration_page = html.Div([
    html.Pre(
            children='Lan configuration page',
        ),
    dcc.Link('Go to home page', href='/'),
    dcc.Link('Network config', href='/network_config'),
])

@app.callback(Output('page-content', 'children'),
                [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return landing_page
    elif pathname =='/network_config':
        return network_statistics_page
    elif pathname == '/lan_config':
        return LAN_configuration_page

if __name__ == '__main__':
    app.run_server(debug=True)