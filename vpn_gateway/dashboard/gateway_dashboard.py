import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.offline as pyo
import plotly.graph_objects as go
from plotly import tools
import socket
import gateway_config as gc
import dash_daq as daq
import time
import random
import subprocess

#vpn data usage, up speed, down speed, connected devices, vpn server, forwarded ports, cpu, ram usage, uptime
#query_vpn_network, connect_vpn, disconnect_vpn, reset_vpn, initialise_vpn
#enable_port_forwarding, change_dhcp_config, connect_ssid

app = dash.Dash(__name__)
app.config['suppress_callback_exceptions']= True

app.layout = html.Div([
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),
    dcc.Interval(
        id='interval-component',
        interval=3000, # 3000 milliseconds = 3 seconds
        n_intervals=0
    ),
    # content will be rendered in this element
    html.Div(id='page-content'),
    html.Div(id='dummy-div')
])

tx = html.Div(
    id="control-panel-speed",
    children=[
        daq.Gauge(
            id="control-panel-speed-component",
            label="Upload",
            min=0,
            max=1000,
            showCurrentValue=True,
            value=0,
            size=175,
            units="kbps",
            color="#fec036",
        )
    ],
    n_clicks=0,
)

rx = html.Div(
    id="control-panel-speed1",
    children=[
        daq.Gauge(
            id="control-panel-speed-component2",
            label="Download",
            min=0,
            max=1000,
            showCurrentValue=True,
            value=0,
            size=175,
            units="kbps",
            color="#fec036",
        )
    ],
    n_clicks=0,
)


landing_page = html.Div(
        id='landing-page',
        children=[

        
            html.Div(
                id="panel-side",
                children=[
                    #top panel
                    html.Div(
                        id='config_top',
                        children=[
                            html.P(
                                id="satellite-dropdown-text", children=["VPN Gateway Dashboard"]
                            ),
                            html.Div(
                                id='nav_buttons',
                                children=[
                                    html.Button(
                                        id="bb1",
                                        children=dcc.Link('Network config', href='/network_config'),
                                        n_clicks=0),
                                    html.Button(
                                        id="bb1",
                                        children=dcc.Link('LAN config', href='/lan_config'),
                                        n_clicks=0)
                                ]
                            ),
                            
                        ]
                    ),
                ]
            ),
            #body
            html.Div(
                id='dashboard_body',
                children=[
                    html.Div(
                        id='div1',
                        children=[
                            html.Div(
                                id='guage-panel',
                                children=[
                                    html.Div(
                                        id='guage-element',
                                        children=[
                                            tx,
                                        ]
                                    ),
                                    html.Div(
                                        id='guage-element',
                                        children=[
                                            rx,
                                        ]
                                    )
                                ]
                            ),
                            html.Div(
                                id='guage-panel',
                                children=[
                                    html.Div(
                                        id='graph-panel'
                                    )

                                ]
                            )
                        ]
                    ),
                    html.Div(
                        id='div2',
                        children=[
                            #connected devices, vpn server, forwarded ports,
                            
                            html.Div(
                                id='div-b',
                                children=[
                                    html.H1(id="satellite-nameE", children=("Connected Devices")),
                                    html.H1(id="satellite-nameE", children=(len(gc.get_connected_devices()))),
                                ]
                            ),
                            html.Div(
                                id='div-b',
                                children=[
                                    html.H1(id="satellite-nameE", children=("Open Ports")),
                                    html.H1(id="satellite-nameE", children=(len(gc.get_open_ports()))),
                                ]
                            ),
                            html.Div(
                                id='div-b',
                                children=[
                                    html.H1(id="satellite-nameE", children=("VPN Server Ip")),
                                    html.H1(id="satellite-nameE", children=(gc.get_connected_server_ip())),
                                ]
                            ),
                            
                        ]
                    ),
                ]
            ) 
    ])


connect_toggle = daq.ToggleSwitch(
    id="connect_toggle",
    value=False,
    label=["Disconnect", "Connect"],
    color="#ffe102",
    style={"color": "#black"},
)

pfconnect_toggle = daq.ToggleSwitch(
    id="pfconnect_toggle",
    value=False,
    label=["Disable", "Enable"],
    color="#ffe102",
    style={"color": "#black"},
)

options_dropdown = dcc.Dropdown(
    id="satellite-dropdown-component",
    options=[
        {"label": "Map Graph", "value": "map_graph"},
        {"label": "VPN Monitoring", "value": "server_stats"},
        {"label": "VPN Gateways", "value": "net_info"},
    ],
    clearable=False,
    value="map_graph",
)

network_statistics_page = html.Div(
        id="network_statistics_page",
        children=[
            html.Div(
                id="panel-side",
                children=[
                    #top panel
                    html.Div(
                        id='config_top',
                        children=[
                            html.P(
                                id="satellite-dropdown-text", children=["VPN Connection"]
                            ),
                            html.Div(
                                id='nav_buttons',
                                children=[
                                    html.Button(
                                        id="bb1",
                                        children=dcc.Link('Go to home page', href='/'),
                                        n_clicks=0),
                                    html.Button(
                                        id="bb1",
                                        children=dcc.Link('Lan config', href='/lan_config'),
                                        n_clicks=0)
                                ]
                            ),
                            
                        ]
                    ),   
                ]),
                
            #body
            html.Div(
                id='ipsec_config_body',
                children=[
                    html.Div(
                        id='div-3',
                        children=[
                            html.Div(
                                id='drop-map-box',
                                children=[
                                    html.Div(
                                        id='drop-map',
                                        children=[
                                        ]
                                    ),
                                     html.Div(
                                        id='drop-map-toggle',
                                        children=[
                                            connect_toggle
                                        ]
                                    ),
                                    
                                ]
                            ),
                            html.Div(
                                id='drop-map-details',
        
                            ),
                        ]
                    ),
                    html.Div(
                        id='div-3',
                        children=[
                            html.Div(
                                id='status-div',
                                children=[
                                    html.P(
                                        id="satellite-dropdown-text", children=["Status: "]
                                    ),
                                    html.P(
                                        id="connection-value",
                                    ),
                                    #html.Div(
                                    #    id='status-div',
                                    #    children=[]
                                    #),
                                ]
                            ),
                            html.Div(
                                id='status-details-div',
                                children=[
                                    
                                    html.P(
                                        id="connection-value",
                                    ),
                                    html.P(
                                        id="satellite-dropdown-text-virtual-ip", 
                                    ),
                                    #html.Div(
                                    #    id='status-div',
                                    #    children=[]
                                    #),
                                ]
                            ),
                        ]
                    )

                ]
            )

        ]
    )


LAN_configuration_page = html.Div(
    id = 'LAN_configuration_page',
    children=[

    
        html.Div(
            id="panel-side",
            children=[
                #top panel
                html.Div(
                    id='config_top',
                    children=[
                        html.P(
                            id="satellite-dropdown-text", children=["LAN Configuration"]
                        ),
                        html.Div(
                            id='nav_buttons',
                            children=[
                                html.Button(
                                        id="bb1",
                                        children=dcc.Link('Go to home page', href='/'),
                                        n_clicks=0),
                                html.Button(
                                        id="bb1",
                                        children=dcc.Link('Network config', href='/network_config'),
                                        n_clicks=0)                
                            ]
                        ),
                        
                    ]
                ),

                
            ]),
        #enable_port_forwarding, change_dhcp_config, connect_ssid
        #body
        html.Div(
            id='lan_config_body',
            children=[
                html.Div(
                    id='wifi_connect_body',
                    children=[
                        html.Div(
                            id='wifi-top',
                            children=[
                                html.P(
                                    id="satellite-dropdown-text", children=["WiFi"]
                                ),
                            ]
                        ),
                        
                        html.Div(
                            id='wifi-middle',
                            children=[
                                #inputs
                                html.Div(
                                    id='ssid_div',
                                    children=[
                                        html.P(
                                            id="satellite-dropdown-textT", children=["WiFi ssid"]
                                        ),
                                    ]
                                ),
                                html.Div(id='ssid_div',
                                    children=[dcc.Input(id="ssid")],className="four columns"),
                                html.Div(
                                    id='ssid_div',
                                    children=[
                                        html.P(
                                            id="satellite-dropdown-textT", children=["passphrase"]
                                        ),
                                    ]
                                ),
                                html.Div(id='ssid_div',
                                    children=[dcc.Input(id="ssid_password")],className="four columns"),
                                html.Div(id='dummy-wifi-bottom'),
                            ]
                        ),
                        html.Div(
                            id='wifi-bottom',
                            children=[
                                #button
                                html.Button(
                                        id="wifi_button",
                                        children="Connect",
                                        #value=host,
                                        n_clicks=0)
                            ]
                        ),
                        html.Div(
                            id='wifi-bottom-end',
                            children=[
                                html.Div(
                                    id='bb-end1',
                                    
                                ),
                                html.Div(
                                    id='bb-end2',
                                    
                                ),
                                
                            ]
                        ),
                    ]
                ),

                html.Div(
                    id='configure_dhcp_body',
                    children=[
                        html.Div(
                            id='dhcp-top',
                            children=[
                                html.P(
                                    id="satellite-dropdown-text", children=["LAN DHCP"]
                                ),
                            ]
                        ),
                        
                        html.Div(
                            id='dhcp-middle',
                            children=[
                                #inputs
                                html.Div(
                                    id='dhcp_input_div1',
                                    children=[
                                        html.P(
                                            id="satellite-dropdown-textT", children=["Start IP"]
                                        ),
                                    ]
                                ),
                                html.Div(id='dhcp_input_div1',
                                    children=[dcc.Input(id="start-ip")],className="four columns"),
                                html.Div(
                                    id='dhcp_input_div1',
                                    children=[
                                        html.P(
                                            id="satellite-dropdown-textT", children=["End IP"]
                                        ),
                                    ]
                                ),
                                html.Div(id='dhcp_input_div1',
                                    children=[dcc.Input(id="end-ip")],className="four columns"),
                            ]
                        ),
                        html.Div(
                            id='dhcp-bottom',
                            children=[
                                #button
                                html.Button(
                                        id="dhcp_configure_button",
                                        children="Configure",
                                        #value=host,
                                        n_clicks=0)
                            ]
                        ),
                        html.Div(id='dummy-dhcp-bottom'),
                        html.Div(
                            id='dhcp-bottom-end',
                            children=[
                                html.Div(
                                    id='b-end1',
                                    children=[
                                        #html.P(
                                        #    id="satellite-dropdown-text", children=["Address Pool"]
                                        #),
                                    ]
                                ),
                                html.Div(
                                    id='b-end2',
                                    
                                ),
                                
                            ]
                        ),
                    ]
                ),

                html.Div(
                    id='port_forward_body',
                    children=[
                        html.Div(
                            id='portf-top',
                            children=[
                                html.P(
                                    id="satellite-dropdown-text", children=["Port Forwarding"]
                                ),
                            ]
                        ),
                        html.Div(
                            id='portf-body',
                            children=[
                                html.Div(
                                    id='port-configure-pan',
                                    children=[
                                        html.Div(
                                            id='fport-toggle-pan',
                                            children=[
                                                pfconnect_toggle
                                            ]
                                        ),
                                        html.Div(
                                            id='fport-toggle-details-pan',
                                            
                                        ),
                                    ]
                                ),
                                html.Div(
                                    id='fport-details-pan',
                                    
                                ),
                                html.Div(
                                    id='dummy-fport-details-pan',
                                    
                                ),
                                
                            ]
                        ),

                    ]
                ),
            ]
        ),
        #side_panel_title,
        #html.Pre(
        #        children='network configuration page',
        #    ),
            
        
    ]
)

#fport-details-pan

@app.callback(
        Output("fport-toggle-details-pan","children"),
        [
            Input('pfconnect_toggle', 'value'),
            Input('url', 'pathname'),
        ])
def display_page(value, pathname):
    if pathname == '/lan_config':
        if value:
            return html.Div(
                children=[
                    #inputs
                    html.Div(
                        id='pf_input_div1',
                        children=[
                            html.P(
                                id="satellite-dropdown-textT", children=["Client IP"]
                            ),
                        ]
                    ),
                    html.Div(id='pf_input_div1',
                        children=[dcc.Input(id="pf-host-ip")],className="four columns"),
                    html.Div(
                        id='pf_input_div1',
                        children=[
                            html.P(
                                id="satellite-dropdown-textT", children=["Port"]
                            ),
                        ]
                    ),
                    html.Div(id='pf_input_div1',
                        children=[dcc.Input(id="pf-host-port")],className="four columns"),
                    #button
                    html.Button(
                        id="pf_button",
                        children="Add",
                        #value=host,
                        n_clicks=0)
                ]
            )

@app.callback(
        Output("dummy-fport-details-pan","children"),
        [
            Input('url', 'pathname'),
            Input('pf_button', 'n_clicks'),
            
        ],
        [
            State("pf-host-ip", "value"),
            State("pf-host-port", "value")
        ])
def display_page(pathname,n, d1, d2):
    if pathname == '/lan_config':
        if d1 != None and d2 != None:
            y = gc.enable_port_forwarding(d2, d1)
            if y:
                gc.store_port(d1, d2)
                print('Successfully added port')
            else:
                print('UNsuccessfull port add')
            

    return ''


@app.callback(
        Output("dummy-dhcp-bottom","children"),
        [
            Input('url', 'pathname'),
            Input('dhcp_configure_button', 'n_clicks'),
            
        ],
        [
            State("start-ip", "value"),
            State("end-ip", "value")
        ])
def display_page(pathname,n, d1, d2):
    if pathname == '/lan_config':
        
        if d1 != None and d2 != None:
            gc.change_dhcp_config(d1, d2)
            print('succefully added dhcp ips')

    return ''


@app.callback(
  
            Output("bb-end1","children"),
            #Output("dummy-wifi-bottom","children"),
       
        [
            Input('url', 'pathname'),
            Input('wifi_button', 'n_clicks'),
            
        ],
        [
            State("ssid", "value"),
            State("ssid_password", "value")
        ])
def display_page(pathname,n, d1, d2):
    if pathname == '/lan_config':
        
        if d1 != None and d2 != None:
            y = gc.connect_wifi(d1, d2)
            
            if y != '':
                return 'Connected to '+y


@app.callback(
        Output("fport-details-pan","children"),
        [
            Input('url', 'pathname'),
            Input('interval-component', 'n_intervals')
        ])
def display_page(pathname,n):
    if pathname == '/lan_config':
        data = gc.get_open_ports()
        display_div = [
            html.Div(
                id="open-ports-label",
                children=[
                    html.Div('Open Ports', className="four columns"),
                ],
            ),
            html.Div(
                id="value-setter-panel-header11",
                children=[
                    html.Div('Client Ip', className="four columns"),
                    html.Div('Port', className="four columns"),
                    
                ],
                className="row",
            )
        ]

        if len(data) > 0:
            
            for i in data:
                

                display_div.append(
                    html.Div(
                        id="value-setter-panel-u11",
                        children=[
                            html.Div(i[0],className="four columns"),
                            html.Div(i[1], className="four columns"),
                            ],
                        className="row",
                    )
                )

        return display_div


@app.callback([
        Output("connection-value","children"),
        Output("satellite-dropdown-text-virtual-ip", "children"),
        ],
        [
            Input('connect_toggle', 'value'),
            Input("satellite-dropdown-component", "value")
        ])
def display_page(value, drop_value):
    if value:
        data = gc.get_available_servers()
        if len(data) > 0:
            
            for i in data:
                if i[0] == drop_value:
                    
                    #use initialise method
                    res, ip = gc.initialise_vpn(i[1], i[2], i[7], i[3])
                    
                    if res:
                        return ['Connected' , ("Virtual IP: "+ip)]
                    else:
                        return ['Disconnected' , ""]

    else:
        if drop_value != None:
            #res = gc.disconnect_vpn('gateway_vpn')
            #if res:
                return ['Disconnected' , ""]

@app.callback(
        Output("drop-map-details","children"),
        [
            Input('url', 'pathname'),
            Input('interval-component', 'n_intervals')
        ])
def display_page(pathname, n):
    if pathname == '/network_config':
        data = gc.get_available_servers()
        display_div = [
            html.Div(
                id="value-setter-panel-header1",
                children=[
                    html.Div('Server', className="four columns"),
                    html.Div('Location', className="four columns"),
                    html.Div('Number Of users', className="four columns"),
                    html.Div('Latency', className="four columns"),
                ],
                className="row",
            )
        ]

        if len(data) > 0:
            
            for i in data:
                

                display_div.append(
                    html.Div(
                        id="value-setter-panel-u1",
                        children=[
                            html.Div(i[0],className="four columns"),
                            html.Div(i[4], className="four columns"),
                            html.Div(i[5], className="four columns"),
                            html.Div(i[6], className="four columns"),
                            ],
                        className="row",
                    )
                )

        return display_div

@app.callback(
        Output("drop-map","children"),
        [
            Input('url', 'pathname'),
        ])
def display_page(pathname):
    if pathname == '/network_config':
        data = gc.get_available_servers()

        
        if len(data) > 0:
            _options = []
            for i in data:
                _options.append({"label": i[0], "value": i[0]})

                

            return dcc.Dropdown(
                    id="satellite-dropdown-component",
                    options=_options,
                    clearable=False,
                    value="map_graph",
                )
        else:
            return 'No Access Servers Available'

@app.callback([
            Output("control-panel-speed-component", "value"),
            Output("control-panel-speed-component2", "value"),
            Output("graph-panel","children"),
        ],
        [
            Input('url', 'pathname'),
            Input('interval-component', 'n_intervals'),
        ])
def display_page(pathname,n):
    res = gc.get_cpu_ram_usage(2)
    
    data = dict()

    data['time_added'] = int(time.time())
    data['cpu'] = res['cpu_percent']
    data['ram'] = res['ram_percent']
    
    root_path = '/root/test_folder/vpn_gateway/'        #for final deployment
    root_path= 'C:/Users/STUART/Documents/project/gateway scripts/github/vpnproject/vpn_gateway/'       #for development testing
    subprocess.run(["chmod", "+x", root_path+"ifconfig_wlan.sh"])
    r4 = subprocess.run([root_path+"ifconfig_wlan.sh"], shell=True)
    file = open(root_path+'logfiles/wlan_details.txt', 'r').readlines()
    rx = 0
    tx = 0
    for i in file:
        if 'inet ' in i:
            virtual_ip = i.split('inet ')[1].split(' netmask')[0] 
        if 'RX packets' in i:
            rx = int(i.split('bytes')[1].split('(')[0])
        if 'TX packets' in i:
            tx = int(i.split('bytes')[1].split('(')[0])


    data['traffic_in'] = rx
    data['traffic_out'] =tx
    data['connected_hosts'] = len(open('/var/lib/misc/dnsmasq.leases', 'r').readlines())
    data['vpn_data_usage'] = 542
    data['connected_server'] = 2

    gc.write_stats(data)
    time_added, cpu, ram, traffic_in, traffic_out, connected_hosts, vpn_data_usage, connected_server = gc.retrive_stats_data()

    time_added = gc.convert_to_datetime(time_added)
    
    if len(time_added) > 50:
        time_added = time_added[(len(time_added)-50):len(time_added)]
        traffic_in = traffic_in[(len(traffic_in)-50):len(traffic_in)]
        traffic_out = traffic_out[(len(traffic_out)-50):len(traffic_out)]
    
    
    fig = dcc.Graph(
        id="histogram-graphq",                        
        figure={
            "data": [
                {
                    "x": time_added,
                    "y": traffic_in,
                    "type": "scatter",
                    "name":"Data In",
                    "marker": {"color": "#89f72f"},
                },
                {
                    "x": time_added,
                    "y": traffic_out,
                    "type": "scatter",
                    "name":"Data Out",
                    "marker": {"color": "#117cf7"},
                }
            ],
            "layout": {
                "margin": {"t": 30, "r": 35, "b": 40, "l": 50},
                "xaxis": {"dtick": 5, "gridcolor": "#636363", "showline": False},
                "yaxis": {"showgrid": False},
                "plot_bgcolor": "#2b2b2b",
                "paper_bgcolor": "#2b2b2b",
                "font": {"color": "gray"},
            },
        },
      config={"displayModeBar": False},
    )

    return [random.randint(0, 500), random.randint(0, 500), fig]
'''
@app.callback(Output('dashboard_body', 'children'),
        [
            Input('url', 'pathname'),
            Input('interval-component', 'n_intervals'),
        ])
def display_page(pathname, n):
    time_added, cpu, ram, traffic_in, traffic_out, connected_hosts, vpn_data_usage, connected_server = gc.retrive_stats_data()
'''


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
    app.run_server(debug=True, host='192.168.43.205')





side_panel_title = html.P(
    id="satellite-dropdown-text", children=["VPN Gateway", html.Br(), " Dashboard"]
)

#network

ip_address_field = html.H1(id="satellite-name", children=("IP : "+socket.gethostbyname(socket.gethostname())))

server_details = html.Div(
    className="satellite-description", id="satellite-description"
)

side_panel_layout = html.Div(
    id="panel-side",
    children=[
        side_panel_title,
        #html.Div(id="satellite-dropdown", children=options_dropdown),
         html.Pre(
            children='Home Page',
        ),
        
        html.Div(id="panel-side-text", children=[ip_address_field, server_details]),
    ],
)

server_statistics = html.Div(
    #id="histogram-container",
    children=[
        html.Div(
            id="histogram-container-graphs",
            children=""
            ),
        html.Div(
            id="histogram-container-graphs2",
            children=""
            )
        ],
)
'''
vpn_gateways = html.Div(
    #id="histogram-container",
    children=[
        html.Div(
            id="gateway-container",
            children=""
            ),
        html.Div(
            id="gateway-container2",
            children=""
            )
        ],
)
'''
main_panel_layout = html.Div(
        id="panel-upper-lower2",
        children=[
            #map_toggle,
            html.Div(
                id="panel-upper-lower",
                children=[

                ]
                )
            ])

root_layout = html.Div(
    id="root",
    children=[
        side_panel_layout,
        main_panel_layout,
    ],
)
#
