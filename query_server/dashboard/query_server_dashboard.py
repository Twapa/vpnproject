import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from datetime import datetime
import plotly.offline as pyo
import plotly.graph_objects as go
from plotly import tools
import dash_daq as daq
import sqlite3
import socket
import json

app = dash.Dash(__name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],)
app.config['suppress_callback_exceptions']= True

app.layout = html.Div([
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),
    dcc.Interval(
        id='interval-component',
        interval=6000, # 6000 milliseconds = 6 seconds
        n_intervals=0
    ),
    # content will be rendered in this element
    html.Div(id='page-content'),
    html.Div(id='dummy-div')
])

def server_location_on_map():
    countries = []
    #db_path = "/root/query_server_new/query_server/vpn_servers.db"
    db_path = "/root/query_server_new/query_server/vpn_servers.db"
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    cursor = db.execute('SELECT * FROM ACCESS_SERVER_STATISTICS')
    for row in cursor:
        countries.append(row[2])

    countries = list(set(countries))
    map_data =[]
    for country in countries:
        cursor = db.execute('SELECT * FROM COUNTRY_MAP_LOCATION WHERE country =?',(country,))
        for row in cursor:
            map_data.append(
                {
                    "type": "scattermapbox",
                    "lat": [row[2]],
                    "lon": [row[1]],
                    "hoverinfo": "text",
                    "text": (row[3]+" "+row[4]),
                    "mode": "markers",
                    "marker": {"size": 10, "color": "#fec036"},
                }
            )
            print(map_data)
    return map_data


# Mapbox
MAPBOX_ACCESS_TOKEN = "pk.eyJ1Ijoic3R1YXJ0MzkiLCJhIjoiY2wxMDJtYXg2MDczeTNqdzF2bXFtN3M5OCJ9.cksZKSy__gdy6-RHj1wbaw"
MAPBOX_STYLE = "mapbox://styles/plotlymapbox/cjyivwt3i014a1dpejm5r7dwr"

map_data = server_location_on_map()

map_toggle = daq.ToggleSwitch(
    id="control-panel-toggle-map",
    value=False,
    label=["Summary", "Details"],
    color="#ffe102",
    style={"color": "#black"},
)
map_layout = {
    "mapbox": {
        "accesstoken": MAPBOX_ACCESS_TOKEN,
        "style": MAPBOX_STYLE,
        "center": {"lat": 45},
    },
    "showlegend": False,
    "autosize": True,
    "paper_bgcolor": "#1e1e1e",
    "plot_bgcolor": "#1e1e1e",
    "margin": {"t": 0, "r": 0, "b": 0, "l": 0},
}
map_graph = html.Div(
    id="world-map-wrapper",
    children=[
        #map_toggle,
        dcc.Graph(
            id="world-map",
            figure={"data": map_data, "layout": map_layout},
            config={"displayModeBar": False, "scrollZoom": False},
        ),
    ],
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
def get_network_details():
    #db_path = "/root/query_server/vpn_servers.db"
    db_path = "/root/query_server_new/query_server/vpn_servers.db"
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    cursor = db.execute('SELECT * FROM REGISTERED_NETWORKS')
    #for row in cursor:
    #    host_names.append(row[1])

def return_server_details(host):
    db_path = "/root/query_server_new/query_server/vpn_servers.db"
    host_names, children, network_id = [], [], []
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row

    print('THE HOST : ',host)
    location, cpu, ram, pks_recieved, pks_lost, min_rtt, avg_rtt, max_rtt, ip_address, total_users, traffic_in, traffic_out = [], [], [], [], [], [], [], [], [], [], [], []
    usernames, passwords, psks, ips = [], [], [], []
    ip_port, tf_in, tf_out = [], [], []
    time_submitted, ipsec_status = [], []
    status, client_ip, ports = [], [], []
    
    cursor = db.execute('SELECT * FROM PORTS WHERE hostname =?', (host,))
    for row in cursor:
        ports.append(row[2])
        client_ip.append(row[3])
        status.append(row[4])

    #get user info
    cursor = db.execute('SELECT * FROM CHAP_SECRETS WHERE hostname =?', (host,))
    for row in cursor:
        usernames.append(row[2])
        passwords.append(row[3])
        psks.append(row[4]) 
        ips.append(row[1])

    cursor = db.execute('SELECT * FROM CLIENT_STATES WHERE hostname =?', (host,))
    for row in cursor:
        ip_port.append(row[1]) 
        tf_in.append(row[2]) 
        tf_out.append(row[3])
    
    cursor = db.execute('SELECT * FROM ACCESS_SERVER_STATISTICS WHERE hostname =?',(host,))
    for row in cursor:
        time_submitted.append(row[0])
        total_users.append(row[3])
        traffic_in.append(row[11])
        traffic_out.append(row[12])
        min_rtt.append(row[15])
        avg_rtt.append(row[16])
        max_rtt.append(row[17])
        ip_address.append(row[18])
        cpu.append(row[13])
        ram.append(row[14])
        location.append(row[2])
        pks_recieved.append(row[19])
        pks_lost.append(row[20])
        ipsec_status.append(row[21])
    print('packet lost : ',pks_lost[len(pks_lost)-1],'packets recieved : ',pks_recieved[len(pks_recieved)-1])

    return time_submitted, location, cpu, ram, pks_recieved, pks_lost, min_rtt, avg_rtt, max_rtt, ip_address, total_users, traffic_in, traffic_out, usernames, passwords, psks, ips, ip_port, tf_in, tf_out, ipsec_status, status, client_ip, ports

def return_gateway_details():
    db_path = "/root/query_server_new/query_server/vpn_servers.db"
    network_id, server_ip, username, password, psk, router_ip = [], [], [], [], [], []
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row

    cursor = db.execute('SELECT * FROM REGISTERED_NETWORKS')
    for row in cursor:
        network_id.append(row[0])
        server_ip.append(row[1])
        username.append(row[2])
        password.append(row[3])
        psk.append(row[4])
        router_ip.append(row[5])
    
    return network_id, server_ip, username, password, psk, router_ip

side_panel_title = html.P(
    id="satellite-dropdown-text", children=[" Query Server", html.Br(), " Dashboard"]
)

ip_address_field = html.H1(id="satellite-name", children=("IP : 88.80.187.189"))

server_details = html.Div(
    className="satellite-description", id="satellite-description"
)

side_panel_layout = html.Div(
    id="panel-side",
    children=[
        side_panel_title,
        html.Div(id="satellite-dropdown", children=options_dropdown),
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

main_panel_layout = html.Div(
        id="panel-upper-lower2",
        children=[
            map_toggle,
            html.Div(
                id="panel-upper-lower",
                children=[
                    map_graph])
            ])

root_layout = html.Div(
    id="root",
    children=[
        side_panel_layout,
        main_panel_layout,
    ],
)
#

@app.callback(Output("gateway-container", 'children'),
              [Input('interval-component', 'n_intervals')])
def update_gateway_details(n):
    network_id, server_ip, username, password, psk, router_ip = return_gateway_details()
    if len(network_id) > 0:
        _children = []
        for i in range(0, len(network_id)):
            _children.append(
                html.Div(
                    id='gateway-panel',
                    children=[
                        html.Div(
                            id='gateway-panel-image-div',
                            children=[
                                html.Img(id='gateway-panel-image', src='assets/gateway_image.png')
                            ]
                        ),
                        html.Div(
                            id='gateway-panel-details',
                            children=[
                                    html.Div(
                                        id="value-setter-panel-header1",
                                        children=[
                                            html.Div('Network Id', className="four columns"),
                                            html.Div('VPN Server IP', className="four columns"),
                                            html.Div('Pre Shared Key', className="four columns"),
                                            html.Div('Router Ip', className="four columns"),
                                        ],
                                        className="row",
                                    ),

                                
                                    html.Div(
                                        id="value-setter-panel-u1",
                                        children=[
                                            html.Div(network_id[i],className="four columns"),
                                            html.Div(server_ip[i], className="four columns"),
                                            html.Div(psk[i], className="four columns"),
                                            html.Div(router_ip[i], className="four columns"),
                                            ],
                                        className="row",
                                        )
                                    
                            ]
                        ),
                    ]
                )
            )
        return _children
    
    else:
        
        return html.Div(
               id='gateway-panel-nimage-div',
               children=[
                   html.Img(id='gateway-panel-image', src='assets/gateway_image_no_found.png')
               ]
            )


@app.callback(Output("satellite-description", 'children'),
              [Input('interval-component', 'n_intervals')])
def update_server_details(n):
    db_path = "/root/query_server_new/query_server/vpn_servers.db"
    host_names, children, network_id, tunnel_count = [], [], [], []
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    cursor = db.execute('SELECT * FROM ACCESS_SERVER_STATISTICS')
    #returns number of servers being tracked
    for row in cursor:
        host_names.append(row[1])

    host_names = list(set(host_names))
    temp = []
    n_tunnels = 0
    for __host in host_names:
        cursor = db.execute('SELECT * FROM ACCESS_SERVER_STATISTICS WHERE hostname =?', (__host,))
        for row in cursor:
            temp.append(row[3])

        if len(temp) > 0:
            n_tunnels += int(temp[len(temp)-1])

    servers_count = len(list(set(host_names)))
    
    #returns number of networks being tracked
    cursor = db.execute('SELECT * FROM REGISTERED_NETWORKS')
    for row in cursor:
        network_id.append(row[0])

    active_networks = 0
    if len(network_id) > 0:
        active_networks = len(network_id)
        
    children.append(html.Div(
        id="xx1",
        children=[html.H1(id="satellite-name", children=("VPN servers : "+ str(servers_count)))]
        )
    )
    children.append(html.Div(
        id="xx1",
        children=[html.H1(id="satellite-name", children=("Active Networks : "+ str(active_networks)))]
        )
    )
    children.append(html.Div(
        id="xx1",
        children=[html.H1(id="satellite-name", children=("Active Users : "+ str(len(network_id))))]
        )
    )
    children.append(html.Div(
        id="xx1",
        children=[html.H1(id="satellite-name", children=("PPP Tunnels : "+ str(n_tunnels)))]
        )
    )
    
    
    
    
    return children

#@app.callback(Output("histogram-container-graphs", 'children'),
#    [
#        Input("server_settings", "n_clicks"), 
#        Input('interval-component', 'n_intervals')
#    ],
#    [State('server_settings', 'value')],)
@app.callback(Output("histogram-container-graphs", 'children'),
    [
        Input('interval-component', 'n_intervals'),
        Input("control-panel-toggle-map", "value"),
    ])
def return_server_stats(n_intervals, toggle):
    #db_path = "/root/query_server/vpn_servers.db"
    db_path = "/root/query_server_new/query_server/vpn_servers.db"
    host_names = []
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    cursor = db.execute('SELECT * FROM ACCESS_SERVER_STATISTICS')
    for row in cursor:
        host_names.append(row[1])

    host_names = list(set(host_names))
    _children =[]
    #toggle = False
    if not toggle:
        for host in host_names:
            time_submitted, location, cpu, ram, pks_recieved, pks_lost, min_rtt, avg_rtt, max_rtt, ip_address, total_users, traffic_in, traffic_out, usernames, passwords, psks, ips, ip_port, tf_in, tf_out, ipsec_status, status, client_ip, ports = return_server_details(host) 

            time_submitted = convert_to_datetime(time_submitted)
            if len(traffic_in) > 70:
                traffic_in = traffic_in[(len(traffic_in)-70):len(traffic_in)]
                traffic_out = traffic_out[(len(traffic_out)-70):len(traffic_out)]
                time_submitted = time_submitted[(len(time_submitted)-70):len(time_submitted)]

            pksl = '0'
           
            _children.append(
            
                    html.Div(
                        id='panel-lower',
                        children=[
                            html.Div(
                                id="histogram-header",
                                children=[
                                    html.H1(
                                        id="histogram-title", children=[(host+" "+str(ip_address[len(ip_address)-1])+" ("+location[len(location)-1]+")")]
                                    ),
                                    html.Button(
                                        id="server_settings",
                                        children="☰",
                                        value=host,
                                        n_clicks=0)
                                ],
                            ),
                            dcc.Graph(
                                id="histogram-graph",
                                figure={
                                    "data": [
                                        {
                                            "x": time_submitted,
                                            "y": traffic_in,
                                            "type": "scatter",
                                            "name":"Data In",
                                            "marker": {"color": "#89f72f"},
                                        },
                                        {
                                            "x": time_submitted,
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
                            ),

                            html.Div(
                                id="panel-lower-x",
                                children=[
                                    #html.Div(id="panel-lower-y", children=''),
                                    html.H1(id="satellite-name2", children=("CPU : "+str(cpu[len(cpu)-1])+'%')),
                                    html.H1(id="satellite-name2", children=("RAM : "+str(ram[len(ram)-1])+'%')),
                                    #html.H1(id="satellite-name2", children=("Minimum Latency : "+str(min_rtt[len(min_rtt)-1]))),
                                    html.H1(id="satellite-name2", children=("Packet Loss : "+pksl+'%')),
                                    html.H1(id="satellite-name2", children=("Response Time : "+str(max_rtt[len(max_rtt)-1]))+"ms"),
                                    html.H1(id="satellite-name2", children=("Connected Users : "+str(total_users[len(total_users)-1]))),
                                    
                                ]
                            ),
                        ]),
                )
        return _children
    else:
        return None

def build_tabs():
    return 

@app.callback(Output("histogram-container-graphs2", 'children'),
    [
        Input("control-panel-toggle-map", "value"),
    ])
def return_server_stats(toggle):
    #db_path = "/root/query_server/vpn_servers.db"
    db_path = "/root/query_server_new/query_server/vpn_servers.db"
    host_names = []
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    cursor = db.execute('SELECT * FROM ACCESS_SERVER_STATISTICS')
    for row in cursor:
        host_names.append(row[1])

    host_names = list(set(host_names))
    _children =[]
    #toggle = False
    if toggle:
        fig = html.Div(
                html.Div(
                    id='someid',
                    children=[
                        html.Div(
                            id="tabs",
                            className="tabs",
                            children=[
                                dcc.Tabs(
                                    id="app-tabs",
                                    value="tab2",
                                    className="custom-tabs",
                                    children=[
                                        dcc.Tab(
                                            id="Specs-tab",
                                            label="Status Details",
                                            value="tab1",
                                            className="custom-tab",
                                            selected_className="custom-tab--selected",
                                        ),
                                        dcc.Tab(
                                            id="Control-chart-tab",
                                            label="Specification Settings",
                                            value="tab2",
                                            className="custom-tab",
                                            selected_className="custom-tab--selected",
                                        ),
                                    ],
                                )
                            ],
                        ),
            
                        html.Div(
                            id='someid',
                            children=[
                                html.Div(
                                    id="settings-menu",
                                    children=[
                                        html.Div(
                                            id="metric-select-menu",
                                            # className='five columns',
                                            children=[
                                                #html.Label(id="metric-select-title", children="Select Server"),
                                                html.Br(),
                                                html.Div(
                                                    id='dropd1', 
                                                    children=[
                                                        html.Div(
                                                            id="value-details-view-output-xx",children=[html.H1(id="satellite-name", children=("Server"))], className="output-datatable"
                                                        ),
                                                        dcc.Dropdown(
                                                            id="metric-select-dropdown",
                                                            options=list(
                                                                {"label": param, "value": param} for param in host_names
                                                            ),
                                                            value=host_names[0],
                                                        ),
                                                    ]
                                                ),        
                                            ],
                                        ),
                                        html.Div(
                                            id="value-setter-menu",
                                            # className='six columns',
                                            children=[
                                                html.Div(id="value-setter-panel"),
                                                html.Br(),
                                                # html.Div(
                                                #     id="button-div",
                                                #     children=[
                                                #         html.Button("Update", id="value-setter-set-btn"),
                                                #         html.Button(
                                                #             "View current setup",
                                                #             id="value-setter-view-btn",
                                                #             n_clicks=0,
                                                #         ),
                                                #     ],
                                                # ),
                                                
                                            ],
                                        ),
                        
                                    ],
                                ),

        
                            ]
                        ),
                        html.Div(
                            id="value-details-view-output", className="output-datatable"
                        ),
                        html.Div(
                            id="value-setter-view-output", className="output-datatable"
                        ),
                        html.Div(
                            id='dropd1',
                            children=[
                                html.Div(
                                    id="value-details-view-output-xx",children='', className="output-datatable"
                                ),
                                html.Div(
                                    id="value-details-view-output-x", className="output-datatable"
                                ),
                            ]
                        ),
                        html.Div(
                            id="value-details-view-output-y", className="output-datatable"
                        ),
                        html.Div(
                            id='hhh',
                            children=[
                                html.Div(
                                    id="value-details-view-output-z", className="output-datatable"
                                ),
                                html.Div(
                                    id="value-details-view-output-z1", className="output-datatable"
                                ),
                                html.Div(
                                    id="value-details-view-output-z2", className="output-datatable"
                                ),
                                html.Div(
                                    id="value-details-view-output-z3", className="output-datatable"
                                ),
                                html.Div(
                                    id="value-details-view-output-z4", className="output-datatable"
                                ),
                                html.Div(
                                    id="value-details-view-output-z5", className="output-datatable"
                                ),
                                html.Div(
                                    id="value-details-view-output-z6", className="output-datatable"
                                ),
                            ]
                        ),
                        html.Div(
                            id='user-container',
                            children=[
                                html.Div(
                                    id="value-details-view-output1", className="output-datatable"
                                ),
                                html.Div(
                                    id="value-setter-view-output1", className="output-datatable"
                                ),
                            ]
                        ),
                        
                    ]        
                )
            )
   
        return fig
    else:
        return None
    
def convert_to_datetime(time_submitted):
    res = []
    for t in time_submitted:
        res.append(datetime.fromtimestamp(t).strftime("%H:%M:%S") )
    return res

#value-details-view-output
@app.callback(
    Output('value-details-view-output', 'children'),
    [
        Input("metric-select-dropdown", "value"), 
        Input('interval-component', 'n_intervals'),
        Input("app-tabs", "value")
    ]
    )
def output(_host, n, tab_value):
    time_submitted, location, cpu, ram, pks_recieved, pks_lost, min_rtt, avg_rtt, max_rtt, ip_address, total_users, traffic_in, traffic_out, usernames, passwords, psks, ips, ip_port, tf_in, tf_out, ipsec_status, status, client_ip, ports = return_server_details(_host)
    # username, ip_port, rx, tx, is_static, vpn_password
    
    if tab_value =='tab1':
        _total_users = 0
        if len(total_users) > 0:
            _total_users = total_users[len(total_users)-1] 


        _time = convert_to_datetime(time_submitted)
        if len(_time) > 40:
            _time = _time[(len(_time)-40):len(_time)]
        
        return html.Div(
            id='detailed-box1',
            children=[
                html.Div(
                    id="detailed-box",
                    children=[
                        html.Div(
                            id='tt2',
                            children=[
                        
                                #tunnels
                                html.Div(
                                    id='yyR',
                                    children=[
                                        html.Div(
                                            id='pad-box',
                                            children=[
                                                html.Div(
                                                    id="detail-element-box",
                                                    children=[str(_total_users)]
                                                ),
                                                html.Div(
                                                    id="detail-element-box1",
                                                    children=[' tunnels']
                                                ),
                                            ]
                                        )
                                    ]
                                ),

                                # users
                                html.Div(
                                    id='yyR',
                                    children=[
                                        html.Div(
                                            id='pad-box',
                                            children=[
                                                html.Div(
                                                    id="detail-element-box",
                                                    children=[str(_total_users)]
                                                ),
                                                html.Div(
                                                    id="detail-element-box1",
                                                    children=[' users']
                                                ),
                                            ]
                                        )
                                    ]
                                ),
                                

                                #status
                                html.Div(
                                    id="yyR",
                                    children=[
                                        html.Div(
                                            id='pad-box',
                                            children=[
                                                html.Div(
                                                    id="detail-element-box",
                                                    children=["Status: "]
                                                ),
                                                html.Div(
                                                    id="detail-element-box1",
                                                    children=[str(ipsec_status[len(ipsec_status)-1])]
                                                ),
                                            ]
                                        )
                                    ]
                                ),



                            ]
                        ),

                        html.Div(
                            id='tt3',
                            children=[
                                html.Div(
                                    id='rxt',
                                    children=[
                                        #ip address
                                        html.Div(
                                            id='yy2',
                                            children=[
                                                html.Div(
                                                    id='pad-box',
                                                    children=[
                                                        html.Div(
                                                                id="detail-element-box",
                                                                children=['IP ']
                                                            ),
                                                        html.Div(
                                                                id="detail-element-box1",
                                                                children=[ip_address[len(ip_address)-1]]
                                                            ),
                                                    ]
                                                )
                                            ]
                                        ),
                                    ]
                                ),
                                
                                html.Div(
                                    id='trx',
                                    children=[
                                        #Tx Rx panel
                                        html.Div(
                                            id='tt4',
                                            children=[
                                                #traffic in
                                                html.Div(
                                                    id='yyT',
                                                    children=[
                                                        html.Div(
                                                            id='pad-box',
                                                            children=[
                                                                    html.Div(
                                                                        id="detail-element-box",
                                                                        children=['Tx  ']
                                                                    ),
                                                                    html.Div(
                                                                        id="detail-element-box1",
                                                                        children=[str(round((traffic_out[len(traffic_out)-1]/1000),3))+'KB']
                                                                    ),
                                                                ]
                                                        )
                                                    ]
                                                ),
                                                
                                                #traffic out
                                                html.Div(
                                                    id='yyT',
                                                    children=[
                                                        html.Div(
                                                            id='pad-box',
                                                            children=[
                                                                html.Div(
                                                                        id="detail-element-box",
                                                                        children=['Rx  ']
                                                                    ),
                                                                html.Div(
                                                                        id="detail-element-box1",
                                                                        children=[str(round((traffic_in[len(traffic_in)-1]/1000),3))+'KB']
                                                                    ),
                                                                ]
                                                            )
                                                        ]
                                                    ),
                                            ]
                                        )
                                    ]
                                ),
                            ]
                        ),
                    ]
                ),

                html.Div(
                        id="detailed-box",
                        children=[
                            html.Div(
                                id='gchart',
                                children=[
                                    dcc.Graph(
                                        id="histogram-graph",
                                        figure={
                                            "data": [
                                                {
                                                    "x": _time,
                                                    "y": total_users,
                                                    "type": "scatter",
                                                    "name":"Data In",
                                                    "marker": {"color": "#89f72f"},
                                                },
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
                                ]
                            )
                        ]
                    )
            ]
        )

    else:
        return ''

@app.callback(
    Output('value-setter-view-output', 'children'),
    [
        Input("metric-select-dropdown", "value"), 
        Input('interval-component', 'n_intervals'),
        Input("app-tabs", "value")
    ]
    )
def output(_host, n, tab_value):
    time_submitted, location, cpu, ram, pks_recieved, pks_lost, min_rtt, avg_rtt, max_rtt, ip_address, total_users, traffic_in, traffic_out, usernames, passwords, psks, ips, ip_port, tf_in, tf_out, ipsec_status, status, client_ip, ports = return_server_details(_host)
    # username, ip_port, rx, tx, is_static, vpn_password
    
    
    if tab_value == 'tab1':
        _total_users = 0
        if len(total_users) > 0:
            _total_users = total_users[len(total_users)-1]

        _children = [
            html.Div(
                id="value-setter-panel-header",
                children=[
                    html.Div('Connected IPs', className="four columns"),
                    html.Div('Traffic In', className="four columns"),
                    html.Div('Traffic Out', className="four columns"),
                ],
                className="row",
            )
        ]
        if len(ip_port) > 0:
            ip_port1 = list(set(ip_port))
            
            for i in ip_port1:
                r, r1, r2 = [], [], []
                for z in range(0,len(ip_port)):
                    if i in ip_port[z]:
                        r.append(ip_port[z])
                        r1.append(tf_in[z])
                        r2.append(tf_out[z])
                
                r = r[len(r)-1]
                r1 = r1[len(r1)-1]
                r2 = r2[len(r2)-1]

                _children.append(
                    html.Div(
                        id="value-setter-panel-u",
                        children=[
                            html.Div(r,className="four columns"),
                            html.Div(r1, className="four columns"),
                            html.Div(r2, className="four columns"),
                        ],
                        className="row",
                    )
                )
        return _children

    else: 
        return ''  


@app.callback(
    Output('value-setter-view-output1', 'children'),
    [
        Input("metric-select-dropdown", "value"), 
        Input("app-tabs", "value")
    ]
    )
def output(_host, tab_value): 
    if tab_value == 'tab2':
        time_submitted, location, cpu, ram, pks_recieved, pks_lost, min_rtt, avg_rtt, max_rtt, ip_address, total_users, traffic_in, traffic_out, usernames, passwords, psks, ips, ip_port, tf_in, tf_out, ipsec_status, status, client_ip, ports = return_server_details(_host)
        
        #usernames, passwords, psks,
        
        _total_users = 0
        if len(total_users) > 0:
            _total_users = total_users[len(total_users)-1]

        _children = [
            html.Div(
                id="value-setter-panel-header-lable",
                children=[
                    html.H1(id='vpn_clients_lable', children=['User Profile'], className="four columns"),
                ],
            ),
            html.Div(
                id="value-setter-panel-header",
                children=[
                    html.Div('Username', className="four columns"),
                    html.Div('Password', className="four columns"),
                    html.Div('Pre Shared key', className="four columns"),
                ],
                className="row",
            )
        ]
        if len(usernames) > 0:
            Qusernames = list(set(usernames))
            for i in Qusernames:
                r, r1, r2 = [], [], []
                for z in range(0,len(usernames)):
                    if i in usernames[z]:
                        r.append(usernames[z])
                        r1.append(passwords[z])
                        r2.append(psks[z])
                
                r = r[len(r)-1]
                r1 = r1[len(r1)-1]
                r2 = r2[len(r2)-1]

                _children.append(
                    html.Div(
                        id="value-setter-panel-u",
                        children=[
                            html.Div(r,className="four columns"),
                            html.Div(r1, className="four columns"),
                            html.Div(r2, className="four columns"),
                        ],
                        className="row",
                    )
                )
        return [html.Div(id='lefty1', children=_children)]
    else:
        return ''

@app.callback(
    Output('value-details-view-output1', 'children'),
    [
        Input("metric-select-dropdown", "value"), 
        Input('interval-component', 'n_intervals'),
        Input("app-tabs", "value")
    ]
    )
def output(_host, n_int, tab_value):
    if tab_value == 'tab2':
        time_submitted, location, cpu, ram, pks_recieved, pks_lost, min_rtt, avg_rtt, max_rtt, ip_address, total_users, traffic_in, traffic_out, usernames, passwords, psks, ips, ip_port, tf_in, tf_out, ipsec_status, status, client_ip, ports = return_server_details(_host)

        status, client_ip, ports
        
        #add user, delete user, change user, change psk, enable port forwarding, disable port forwarding

        _children = [
            html.Div(
                id="value-setter-panel-header-lable",
                children=[
                    html.H1(id='vpn_clients_lable', children=['Connected Users'], className="four columns"),
                ],
            ),
            html.Div(
                id="value-setter-panel-header",
                children=[
                    html.Div('Client IP', className="four columns"),
                    html.Div('Port', className="four columns"),
                    html.Div('Status', className="four columns"),
                ],
                className="row",
            )
        ]
        if len(client_ip) > 0:
            Zclient_ip = list(set(client_ip))

            for i in Zclient_ip:
                r, r1, r2 = [], [], []
                for z in range(0,len(client_ip)):
                    if i in client_ip[z]:
                        r.append(client_ip[z])
                        r1.append(ports[z])
                        r2.append(status[z])
                
                r = r[len(r)-1]
                r1 = r1[len(r1)-1]
                r2 = r2[len(r2)-1]

            #for i in range(0, len(client_ip)):
                _children.append(
                    html.Div(
                        id="value-setter-panel-u",
                        children=[
                            html.Div(r,className="four columns"),
                            html.Div(r1, className="four columns"),
                            html.Div(r2, className="four columns"),
                        ],
                        className="row",
                    )
                )
        
        return _children
    else:
        return ''

@app.callback(
    Output('value-details-view-output-xx', 'children'),
    [
        Input("metric-select-dropdown", "value"), 
        Input("app-tabs", "value")
    ]
    )
def output(_host, tab_value):
    if tab_value == 'tab2':
        return [html.H1(id="satellite-name", children=("Option"))]

@app.callback(
    Output('value-details-view-output-x', 'children'),
    [
        Input("metric-select-dropdown", "value"), 
        Input("app-tabs", "value")
    ]
    )
def output(_host, tab_value):
    if tab_value == 'tab2':
        time_submitted, location, cpu, ram, pks_recieved, pks_lost, min_rtt, avg_rtt, max_rtt, ip_address, total_users, traffic_in, traffic_out, usernames, passwords, psks, ips, ip_port, tf_in, tf_out, ipsec_status, status, client_ip, ports = return_server_details(_host)

        #add user, delete user, change user, change psk, enable port forwarding, disable port forwarding
        _options = ['add user', 'delete user', 'change user', 'change psk', 'assign static ip','enable port forwarding', 'disable port forwarding']
        #return html.Div()
        return dcc.Dropdown(
            id="metric-select-dropdown2",
            options=list(
                {"label": param, "value": param} for param in _options
            ),
            value=_options[1],
        )

@app.callback(
    Output('value-details-view-output-y', 'children'),
    [
        Input("metric-select-dropdown", "value"), 
        Input("metric-select-dropdown2", "value"), 
        Input("app-tabs", "value")
    ]
    )
def output(_host, drop_value, tab_value):
    if tab_value == 'tab2':
        time_submitted, location, cpu, ram, pks_recieved, pks_lost, min_rtt, avg_rtt, max_rtt, ip_address, total_users, traffic_in, traffic_out, usernames, passwords, psks, ips, ip_port, tf_in, tf_out, ipsec_status, status, client_ip, ports = return_server_details(_host)

        if drop_value == 'add user':
            return html.Div(
                id="value-setter-panel-uv",
                children=[
                    html.Div(id='add_users_label',children=[html.H1(id="satellite-name", children=('Username'))],className="four columns"),
                    html.Div(id='add_user_input',
                        children=[dcc.Input(id="username")],className="four columns"),
                    html.Div(id='add_users_label',children=[html.H1(id="satellite-name", children=('Password'))],className="four columns"),
                    html.Div(id='add_user_input',
                        children=[dcc.Input(id="password")],className="four columns"),
                    html.Button(
                        id='submit-button',
                        n_clicks=0,
                        children='Add',
                        #style={'fontSize':28}
                    ),
                ],
                className="row",
            )
        elif drop_value == 'delete user':
            return html.Div(
                id="value-setter-panel-uv",
                children=[
                    html.Div(id='del_users_label',children=[html.H1(id="satellite-name", children=('Username'))],className="four columns"),
                    html.Div(id='del_user_input',
                        children=[dcc.Input(id="del_username")],className="four columns"),
                    html.Button(
                        id='del_submit-button',
                        n_clicks=0,
                        children='Delete',
                        #style={'fontSize':28}
                    ),
                ],
                className="row",
            )
        elif drop_value == 'change user':
            return html.Div(
                id="value-setter-panel-uv",
                children=[
                    html.Div(id='cha_users_label',children=[html.H1(id="satellite-name", children=('Username'))],className="four columns"),
                    html.Div(id='cha_user_input',
                        children=[dcc.Input(id="cusername")],className="four columns"),
                    html.Div(id='cha_users_label',children=[html.H1(id="satellite-name", children=('Password'))],className="four columns"),
                    html.Div(id='cha_user_input',
                        children=[dcc.Input(id="cpassword")],className="four columns"),
                    html.Button(
                        id='csubmit-button',
                        n_clicks=0,
                        children='change',
                        #style={'fontSize':28}
                    ),
                ],
                className="row",
            )
        elif drop_value == 'change psk':
            return html.Div(
                id="value-setter-panel-uv",
                children=[
                    html.Div(id='psk_users_label',children=[html.H1(id="satellite-name", children=('New Pre Shared Key'))],className="four columns"),
                    html.Div(id='psk_user_input',
                        children=[dcc.Input(id="psk")],className="four columns"),
                    html.Button(
                        id='psk_submit-button',
                        n_clicks=0,
                        children='Change',
                        #style={'fontSize':28}
                    ),
                ],
                className="row",
            )
            
        elif drop_value == 'assign static ip':
            return html.Div(
                id="value-setter-panel-uv",
                children=[
                    html.Div(id='ip_users_label',children=[html.H1(id="satellite-name", children=('Username'))],className="four columns"),
                    html.Div(id='ip_user_input',
                        children=[dcc.Input(id="susername")],className="four columns"),
                    html.Div(id='ip_users_label',children=[html.H1(id="satellite-name", children=('Password'))],className="four columns"),
                    html.Div(id='ip_user_input',
                        children=[dcc.Input(id="spassword")],className="four columns"),
                    html.Div(id='ip_users_label',children=[html.H1(id="satellite-name", children=('IP'))],className="four columns"),
                    html.Div(id='ip_user_input',
                        children=[dcc.Input(id="sIP")],className="four columns"),
                    html.Button(
                        id='ssubmit-button',
                        n_clicks=0,
                        children='Submit',
                        #style={'fontSize':28}
                    ),
                ],
                className="row",
            )
        elif drop_value == 'enable port forwarding':
            return html.Div(
                id="value-setter-panel-uv",
                children=[
                    html.Div(id='port_users_label',children=[html.H1(id="satellite-name", children=('Client IP'))],className="four columns"),
                    html.Div(id='port_user_input',
                        children=[dcc.Input(id="client_ip")],className="four columns"),
                    html.Div(id='port_users_label',children=[html.H1(id="satellite-name", children=('Port'))],className="four columns"),
                    html.Div(id='port_user_input',
                        children=[dcc.Input(id="port")],className="four columns"),
                    html.Button(
                        id='ipsubmit-button',
                        n_clicks=0,
                        children='Enable',
                        #style={'fontSize':28}
                    ),
                ],
                className="row",
            )
        elif drop_value == 'disable port forwarding':
            return html.Div(
                id="value-setter-panel-uv",
                children=[
                    html.Div(id='dport_users_label',children=[html.H1(id="satellite-name", children=('Client IP'))],className="four columns"),
                    html.Div(id='dport_user_input',
                        children=[dcc.Input(id="dclient_ip")],className="four columns"),
                    html.Div(id='dport_users_label',children=[html.H1(id="satellite-name", children=('Port'))],className="four columns"),
                    html.Div(id='dport_user_input',
                        children=[dcc.Input(id="dport")],className="four columns"),
                    html.Button(
                        id='dipsubmit-button',
                        n_clicks=0,
                        children='Disable',
                        #style={'fontSize':28}
                    ),
                ],
                className="row",
            )
        
        
@app.callback(
    Output('value-details-view-output-z', 'children'),
    [
        Input("metric-select-dropdown", "value"), 
        Input('del_submit-button', 'n_clicks')
    ],
    [
        State('del_username', 'value'),
    ]
    )
def output(_host, n, v1):
    time_submitted, location, cpu, ram, pks_recieved, pks_lost, min_rtt, avg_rtt, max_rtt, ip_address, total_users, traffic_in, traffic_out, usernames, passwords, psks, ips, ip_port, tf_in, tf_out, ipsec_status, status, client_ip, ports = return_server_details(_host)
    server_addr = ip_address[len(ip_address)-1]
    port = 1777
    
    if v1 != None:
            data=dict()
            data= {'action':'delete_user', 'username':v1}
            jsonResult = json.dumps(data).encode('ascii')

            try:
                sock = socket.socket()
            except socket.error as err:
                print('Socket error because of %s' %(err))

            try:
                sock.connect((server_addr, port))
                sock.send(jsonResult)
                #connection.sendall(json.dumps(data).encode('ascii'))
                print('DATA SEND SUCCESSFULLY')
            except socket.gaierror:
                print('There an error resolving the host')

@app.callback(
    Output('value-details-view-output-z1', 'children'),
    [
        Input("metric-select-dropdown", "value"), 
        Input('submit-button', 'n_clicks')
    ],
    [
        State('username', 'value'),
        State('password', 'value'),
    ]
    )
def output(_host, n, v1, v2):
    time_submitted, location, cpu, ram, pks_recieved, pks_lost, min_rtt, avg_rtt, max_rtt, ip_address, total_users, traffic_in, traffic_out, usernames, passwords, psks, ips, ip_port, tf_in, tf_out, ipsec_status, status, client_ip, ports = return_server_details(_host)
    
    server_addr = ip_address[len(ip_address)-1]
    port = 1777
    
    if v1 != None:
        if v2 != None:
            data=dict()
            data= {'action':'add_user', 'username':v1, 'password':v2}
            jsonResult = json.dumps(data).encode('ascii')


            try:
                sock = socket.socket()
            except socket.error as err:
                print('Socket error because of %s' %(err))

            try:
                sock.connect((server_addr, port))
                sock.send(jsonResult)
                #connection.sendall(json.dumps(data).encode('ascii'))
                print('DATA SEND SUCCESSFULLY')
            except socket.gaierror:
                print('There an error resolving the host')

@app.callback(
    Output('value-details-view-output-z2', 'children'),
    [
        Input("metric-select-dropdown", "value"), 
        Input('ssubmit-button', 'n_clicks')
    ],
    [
        State('susername', 'value'),
        State('spassword', 'value'),
        State('sIP', 'value'),
    ]
    )
def output(_host, n, v1, v2, v3):
    time_submitted, location, cpu, ram, pks_recieved, pks_lost, min_rtt, avg_rtt, max_rtt, ip_address, total_users, traffic_in, traffic_out, usernames, passwords, psks, ips, ip_port, tf_in, tf_out, ipsec_status, status, client_ip, ports = return_server_details(_host)
    
    server_addr = ip_address[len(ip_address)-1]
    port = 1777
    
    if v1 != None:
        if v2 != None:
            if v3 != None:
                data=dict()
                data= {'action':'assign_static_ip', 'username':v1, 'password':v2, 'ip_address':v3}
                jsonResult = json.dumps(data).encode('ascii')


                try:
                    sock = socket.socket()
                except socket.error as err:
                    print('Socket error because of %s' %(err))

                try:
                    sock.connect((server_addr, port))
                    sock.send(jsonResult)
                    #connection.sendall(json.dumps(data).encode('ascii'))
                    print('DATA SEND SUCCESSFULLY')
                except socket.gaierror:
                    print('There an error resolving the host')

@app.callback(
    Output('value-details-view-output-z3', 'children'),
    [
        Input("metric-select-dropdown", "value"), 
        Input('csubmit-button', 'n_clicks')
    ],
    [
        State('cusername', 'value'),
        State('cpassword', 'value'),
    ]
    )
def output(_host, n, v1, v2):
    time_submitted, location, cpu, ram, pks_recieved, pks_lost, min_rtt, avg_rtt, max_rtt, ip_address, total_users, traffic_in, traffic_out, usernames, passwords, psks, ips, ip_port, tf_in, tf_out, ipsec_status, status, client_ip, ports = return_server_details(_host)
    
    server_addr = ip_address[len(ip_address)-1]
    port = 1777
    
    if v1 != None:
        if v2 != None:
            data=dict()
            data= {'action':'change_user', 'username':v1, 'password':v2}
            jsonResult = json.dumps(data).encode('ascii')


            try:
                sock = socket.socket()
            except socket.error as err:
                print('Socket error because of %s' %(err))

            try:
                sock.connect((server_addr, port))
                sock.send(jsonResult)
                #connection.sendall(json.dumps(data).encode('ascii'))
                print('DATA SEND SUCCESSFULLY')
            except socket.gaierror:
                print('There an error resolving the host')

@app.callback(
    Output('value-details-view-output-z4', 'children'),
    [
        Input("metric-select-dropdown", "value"), 
        Input('psk_submit-button', 'n_clicks')
    ],
    [
        State('psk', 'value'),
    ]
    )
def output(_host, n, v1):
    time_submitted, location, cpu, ram, pks_recieved, pks_lost, min_rtt, avg_rtt, max_rtt, ip_address, total_users, traffic_in, traffic_out, usernames, passwords, psks, ips, ip_port, tf_in, tf_out, ipsec_status, status, client_ip, ports = return_server_details(_host)
    server_addr = ip_address[len(ip_address)-1]
    port = 1777
    
    if v1 != None:
            data=dict()
            data= {'action':'change_psk', 'psk':v1}
            jsonResult = json.dumps(data).encode('ascii')

            try:
                sock = socket.socket()
            except socket.error as err:
                print('Socket error because of %s' %(err))

            try:
                sock.connect((server_addr, port))
                sock.send(jsonResult)
                #connection.sendall(json.dumps(data).encode('ascii'))
                print('DATA SEND SUCCESSFULLY')
            except socket.gaierror:
                print('There an error resolving the host')

@app.callback(
    Output('value-details-view-output-z5', 'children'),
    [
        Input("metric-select-dropdown", "value"), 
        Input('ipsubmit-button', 'n_clicks')
    ],
    [
        State('client_ip', 'value'),
        State('port', 'value'),
    ]
    )
def output(_host, n, v1, v2):
    time_submitted, location, cpu, ram, pks_recieved, pks_lost, min_rtt, avg_rtt, max_rtt, ip_address, total_users, traffic_in, traffic_out, usernames, passwords, psks, ips, ip_port, tf_in, tf_out, ipsec_status, status, client_ip, ports = return_server_details(_host)
    server_addr = ip_address[len(ip_address)-1]
    port = 1777
    
    if v1 != None:
        if v2 != None:
            data=dict()
            data= {'action':'enable_port_forward', 'ip_address':v1, 'port':v2}
            jsonResult = json.dumps(data).encode('ascii')

            try:
                sock = socket.socket()
            except socket.error as err:
                print('Socket error because of %s' %(err))

            try:
                sock.connect((server_addr, port))
                sock.send(jsonResult)
                #connection.sendall(json.dumps(data).encode('ascii'))
                print('DATA SEND SUCCESSFULLY')
            except socket.gaierror:
                print('There an error resolving the host')

@app.callback(
    Output('value-details-view-output-z6', 'children'),
    [
        Input("metric-select-dropdown", "value"), 
        Input('dipsubmit-button', 'n_clicks')
    ],
    [
        State('dclient_ip', 'value'),
        State('dport', 'value'),
    ]
    )
def output(_host, n, v1, v2):
    time_submitted, location, cpu, ram, pks_recieved, pks_lost, min_rtt, avg_rtt, max_rtt, ip_address, total_users, traffic_in, traffic_out, usernames, passwords, psks, ips, ip_port, tf_in, tf_out, ipsec_status, status, client_ip, ports = return_server_details(_host)
    server_addr = ip_address[len(ip_address)-1]
    port = 1777
    
    if v1 != None:
        if v2 != None:
            data=dict()
            data= {'action':'disable_port_forward', 'ip_address':v1, 'port':v2}
            jsonResult = json.dumps(data).encode('ascii')

            try:
                sock = socket.socket()
            except socket.error as err:
                print('Socket error because of %s' %(err))

            try:
                sock.connect((server_addr, port))
                sock.send(jsonResult)
                #connection.sendall(json.dumps(data).encode('ascii'))
                print('DATA SEND SUCCESSFULLY')
            except socket.gaierror:
                print('There an error resolving the host')

@app.callback(
    Output("panel-upper-lower", "children"),
    [Input("satellite-dropdown-component", "value")],
)
def update_satellite_name(val):
    if val == "map_graph":
        return map_graph
    elif val == "server_stats":
        return server_statistics
    else:
        return vpn_gateways


@app.callback(Output('page-content', 'children'),
                [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return root_layout
    #elif pathname =='/network_config':
    #    return network_statistics_page
    #elif pathname == '/lan_config':
    #    return LAN_configuration_page

if __name__ == '__main__':
    app.run_server(debug=False, host='88.80.187.189')       #app  runs on query server ip