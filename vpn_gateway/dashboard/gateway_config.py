'''
this script contains helper functions that will be used by
the GUI framework to make configuration changes on the router.
All functions will return True if they run successfully and return False otherwise
'''
import subprocess
import json
import socket
import sqlite3
import json
import psutil
import time
from datetime import datetime
import socket

root_path = '/root/test_folder/vpn_gateway/'
root_path= 'C:/Users/STUART/Documents/project/gateway scripts/github/vpnproject/vpn_gateway/'

server_addr, port = '88.80.187.189', 1500               #socket of the query server

def get_available_servers():
    data = {'connection_request':'query_servers'}
    jsonResult = json.dumps(data).encode('ascii')
    try:
        sock = socket.socket()
    except socket.error as err:
        print('Socket error because of %s' %(err))
        return []

    try:
        sock.connect((server_addr, 3000))
        sock.send(jsonResult)
        #connection.sendall(json.dumps(data).encode('ascii'))
        recv_data = sock.recv(4026)
        print('Query Server sent:',recv_data)
        res =  json.loads(recv_data.decode('ascii'))

        server_list = []
        y=[]
        if len(res) > 0:
            for i in res:
                if len(i) > 0:
                    z = i[0]
                
                    y.append([z.split('$$$')[0] , z.split('$$$')[1], z.split('$$$')[2], z.split('$$$')[3], z.split('$$$')[4], z.split('$$$')[5], z.split('$$$')[6],  z.split('$$$')[7]])
                

        sock.close()
        return y
    except socket.gaierror:
        print('There an error resolving the host')
        return []
    

def get_open_ports():
    clients = []
    db = sqlite3.connect(root_path+'gateway_stats.db')
    db.row_factory = sqlite3.Row
    cursor = db.execute('SELECT * FROM PORTS')
    for row in cursor:
        clients.append([row[0],row[1]])
    
    return clients

def store_port(host_ip, port):
    db = sqlite3.connect(root_path+'gateway_stats.db')

    db.execute('INSERT INTO PORTS VALUES (?, ?)', (host_ip, port))
    db.commit()

def get_connected_devices():
    ips = []
    db = sqlite3.connect(root_path+'gateway_stats.db')
    db.row_factory = sqlite3.Row
    cursor = db.execute('SELECT * FROM CONNECTED_USERS')
    for row in cursor:
        ips.append(row[0])
    
    return ips

def get_connected_server_ip():
    ips = []
    db = sqlite3.connect(root_path+'gateway_stats.db')
    db.row_factory = sqlite3.Row
    cursor = db.execute('SELECT * FROM CONNECTED_SERVER')
    for row in cursor:
        ips.append(row[1])
        
    if len(ips) > 0:
        return ips[len(ips)-1]
    else:
        return 'None'

def convert_to_datetime(time_submitted):
    res = []
    for t in time_submitted:
        res.append(datetime.fromtimestamp(t).strftime("%H:%M:%S") )
    return res

def write_stats(data):
    db = sqlite3.connect(root_path+'gateway_stats.db')
    values=(
        data['time_added'],
        data['cpu'],
        data['ram'],
        data['traffic_in'],
        data['traffic_out'],
        data['connected_hosts'],
        data['vpn_data_usage'],
        data['connected_server'],
    )
    db.execute('INSERT INTO STATS(time_added, cpu, ram, traffic_in, traffic_out, connected_hosts, vpn_data_usage, connected_server) ' +\
        'VALUES (?,?,?,?,?,?,?,?)', values)
    db.commit()

def retrive_stats_data():
    db = sqlite3.connect(root_path+'gateway_stats.db')
    time_added, cpu, ram, traffic_in, traffic_out, connected_hosts, vpn_data_usage, connected_server =[], [], [], [], [], [], [], []
    #temp = None

    db.row_factory = sqlite3.Row
    cursor = db.execute('SELECT * FROM STATS')
    for row in cursor:
        time_added.append(row[0])
        cpu.append(row[1])
        ram.append(row[2])
        traffic_in.append(row[3])
        traffic_out.append(row[4])
        connected_hosts.append(row[5])
        vpn_data_usage.append(row[6])
        connected_server.append(row[7])

    return time_added, cpu, ram, traffic_in, traffic_out, connected_hosts, vpn_data_usage, connected_server

def get_bandwidth():        #returns the total bytes sent and recieved by the server
    # Get net in/out
    net1_out = psutil.net_io_counters().bytes_sent
    net1_in = psutil.net_io_counters().bytes_recv

    time.sleep(1)

    # Get new net in/out
    net2_out = psutil.net_io_counters().bytes_sent
    net2_in = psutil.net_io_counters().bytes_recv

    # Compare and get current speed
    if net1_in > net2_in:
        current_in = 0
    else:
        current_in = net2_in - net1_in

    if net1_out > net2_out:
        current_out = 0
    else:
        current_out = net2_out - net1_out

    return {"traffic_in" : 500, "traffic_out" : 450}
    #return {"traffic_in" : current_in, "traffic_out" : current_out}
     

def get_cpu_ram_usage(_time_interval):      #returns cpu and ram usage
    cpu_percent = psutil.cpu_percent(_time_interval)    #measured over a specific time interval
    ram_percent = psutil.virtual_memory()[2]
    usage = {"cpu_percent":cpu_percent, "ram_percent":ram_percent}
    return usage

def send_to_query_server(data:dict, server_addr, port):
    #send key performance metrics, connection statistics to the query server
    jsonResult = json.dumps(data).encode('ascii')
    try:
        sock = socket.socket()
    except socket.error as err:
        print('Socket error because of %s' %(err))

    try:
        sock.connect((server_addr, port))
        sock.send(jsonResult)
        #connection.sendall(json.dumps(data).encode('ascii'))
    except socket.gaierror:
        print('There an error resolving the host')

#def get_vpn_connection_status():

def initialise_vpn(username, password, server_ip, psk):

    subprocess.run(["service", "ipsec", "restart"])
    subprocess.run(["service", "xl2tpd", "restart"])
    script_file = open((root_path+'init_connections.sh'), 'w')
    script_file.writelines([
        'cat > /etc/ipsec.conf <<EOF\n',
        '# ipsec.conf - strongSwan IPsec configuration file\n',
        'conn gateway_vpn\n',
        '    auto=add\n',
        '    keyexchange=ikev1\n',
        '    authby=secret\n',
        '    type=transport\n',
        '    left=%defaultroute\n',
        '    leftprotoport=17/1701\n',
        '    rightprotoport=17/1701\n',
        '    right='+server_ip+'\n',
        '    ike=aes128-sha1-modp2048\n',
        '    esp=aes128-sha1\n',
        'EOF\n',
        '\n',
        'cat > /etc/ipsec.secrets <<EOF\n',
        ': PSK "'+psk+'"\n',
        'EOF\n',
        '\n',
        'chmod 600 /etc/ipsec.secrets\n',
        '\n',
        'cat > /etc/xl2tpd/xl2tpd.conf <<EOF\n',
        '[lac gateway_vpn]\n',
        'lns = 107.172.197.127\n',
        'ppp debug = yes\n',
        'pppoptfile = /etc/ppp/options.l2tpd.client\n',
        'length bit = yes\n',
        'EOF\n',
        '\n',
        'cat > /etc/ppp/options.l2tpd.client <<EOF\n',
        'ipcp-accept-local\n',
        'ipcp-accept-remote\n',
        'refuse-eap\n',
        'require-chap\n',
        'noccp\n',
        'noauth\n',
        'mtu 1280\n',
        'mru 1280\n',
        'noipdefault\n',
        'defaultroute\n',
        'usepeerdns\n',
        'connect-delay 5000\n',
        'name "'+username+'"\n',
        'password "'+password+'"\n',
        'EOF\n',
        '\n',
        'chmod 600 /etc/ppp/options.l2tpd.client\n',
        '\n',
        'service ipsec restart\n',
        'service xl2tpd restart\n',
    ])
    script_file.close()
    #carries out necessary configurations prior to system startup
    subprocess.run(["chmod", "+x", root_path+"init_connections.sh"])
    res = subprocess.run([root_path+"init_connections.sh"], shell=True)
    
    if res.returncode ==0:

        status = connect_vpn('gateway_vpn')

        print('CONNECTION REQUEST STATUS', status)
        
        if status:

            #route add
            f = open(root_path+'route_add.sh', 'w')

            time.sleep(2)

            file = open(root_path+'logfiles/wlan_details.txt', 'r').readlines()
            _ip = None
            for i in file:
                if 'inet ' in i:
                    _ip = i.split('inet ')[1].split(' netmask')[0] 

            e = _ip.split('.')
            q = ''
            for i in range(0,3):
                q += (e[i]+'.')
            q+='1'

            f.write('route add '+server_ip+' gw '+q+'\n')
            f.close()

            f = open(root_path+'route_add1.sh', 'w')
            f.write('route add default dev ppp0\n')
            f.close()

            res = subprocess.run(["chmod", "+x", root_path+"route_add.sh"])
            res = subprocess.run([root_path+"route_add.sh"], shell=True)

            time.sleep(3)

            res = subprocess.run(["chmod", "+x", root_path+"route_add1.sh"])
            res = subprocess.run([root_path+"route_add1.sh"], shell=True)

            if res.returncode ==0:

                #ip forwarding
                subprocess.run(["chmod", "+x", root_path+"gateway_ip_forward.sh"])
                subprocess.run([root_path+"gateway_ip_forward.sh"], shell=True)

                subprocess.run(["iptables", "-t", "nat", "-A", "POSTROUTING", "-o", "ppp0", "-j", "MASQUERADE"])
                subprocess.run(["iptables", "-A", "FORWARD", "-i", "eth0", "-o", "ppp0", "-j", "ACCEPT"])
                subprocess.run(["iptables", "-A", "FORWARD", "-i", "ppp0", "-o", "eth0", "-m", "state", "--state", "RELATED,ESTABLISHED", "-j", "ACCEPT"])
                subprocess.run(["iptables", "-A", "INPUT", "-i", "lo", "-j", "ACCEPT"])
                subprocess.run(["iptables", "-A", "INPUT", "-i", "eth0", "-p", "icmp", "-j", "ACCEPT"])
                subprocess.run(["iptables", "-A", "INPUT", "-i", "eth0", "-p", "tcp", "--dport", "22" ,"-j", "ACCEPT"])
            
                data = dict()
                ip, rx, tx = get_virtual_interface()
                data["network_id"] = ip + '_GATEWAY'
                data["server_ip"] = server_ip
                data["username"] = username
                data["password"] = password
                data["psk"] = psk
                
                data["router_ip"] = ip
                data['connection_request'] = 'register'

                db = sqlite3.connect(root_path+'gateway_stats.db')

                db.execute('INSERT INTO CONNECTED_SERVER VALUES (?, ?)', ('a', server_ip))
                db.commit()
                
                send_to_query_server(data, server_addr, 3000)

                print('SUCCESSFULLY CONNECTED TO THE VPN SERVER')

                return True, ip
            else:
                print('FAILED STEP 3')
                return False, ''
        else:
            print('FAILED STEP 2')
            return False, ''
    else:
        print('FAILED STEP 1')
        return False, ''

def connect_wifi(ssid, password):
    f = open(root_path+'wifi_connect.sh', 'w')
    f.write('wpa_passphrase "'+ssid+'" "'+password+'"\n')
    f.write('wpa_supplicant -c /etc/wpa_supplicant.conf -i wlan0')
    f.close()
    subprocess.run(["chmod", "+x", root_path+"wifi_connect.sh"])
    res = subprocess.run([root_path+"wifi_connect.sh"], shell=True)
    if res.returncode ==0:
        res4 = subprocess.run([root_path+"ifconfig_wlan.sh"], shell=True)
        file = open(root_path+'logfiles/wlan_details.txt', 'r').readlines()
        _ip = None
        for i in file:
            if 'inet' in i:
                _ip = i.split('inet ')[1].split(' netmask')[0] 

        return _ip
    else:
        return ''

def get_virtual_interface():
    subprocess.run(["chmod", "+x", root_path+"logfiles/ifconfig_ppp0.sh"])
    res = subprocess.run([root_path+"logfiles/ifconfig_ppp0.sh"], shell=True)
    if res.returncode ==0: 
        file = open(root_path+'logfiles/ppp0_details.txt', 'r').readlines()
        virtual_ip = None
        rx = 0
        tx = 0
        for i in file:
            if 'inet ' in i:
                virtual_ip = i.split('inet ')[1].split(' netmask')[0] 
            if 'RX packets' in i:
                rx = int(i.split('bytes')[1].split('(')[0])
            if 'TX packets' in i:
                tx = int(i.split('bytes')[1].split('(')[0])

        return virtual_ip, rx, tx
        
def change_l2tp_options(params:dict):
    #changes the setting in the options.l2tpd.client
    pass

def change_l2tp_server(params:dict):
    #changes settings in the xl2tpd.conf file
    pass

def change_psk(psk):
    #changes the pre shared key
    try:
        secrets_files = open("/etc/ipsec.secrets","w")
        secrets_files.write(": PSK \""+psk+"\"")
        secrets_files.close()

        return True
    except:
        return False

def add_vpn_connection(params:dict):
    #changes the settings in the ipsec.conf file
    pass

def change_dhcp_config(start_ip, end_ip):
    #changes settings in the dhcpcd.conf and dnsmasq.conf files
    file = open('/etc/dnsmasq.conf', 'w')
    file.write('interface=eth0\n')
    file.write('bind-dynamic\n')
    file.write('domain-needed\n')
    file.write('bogus-priv\n')
    file.write('dhcp-range='+start_ip+','+end_ip+',255.255.255.0,12h\n')
    file.close()
    pass

def change_route(vpn_server_ip, dafault_gateway_ip):
    #changes the default tunneling route and interface name
    res = subprocess.run(["route", "add", vpn_server_ip , "gw", dafault_gateway_ip])
    if res.returncode ==0:
        return True
    else:
        return False

def reset_vpn(vpn_name):
    res1 = subprocess.run(["service", "ipsec", "restart"])
    res2 = subprocess.run(["service", "xl2tpd", "restart"])
    res3 = subprocess.run(["ipsec", "up", vpn_name])

    try:
        l2tp_file = open("/var/run/xl2tpd/l2tp-control", "w")
        l2tp_file.write("c "+vpn_name)
        l2tp_file.close()

        if res1.returncode ==0 and res2.returncode==0 and res3.returncode==0:     #returns True if all the terminal commands have excuted successfully
            return True
        else:
           return False
    except:
        return False

def connect_vpn(vpn_name):
    res = subprocess.run(["ipsec", "up", vpn_name])

    try:
        l2tp_file = open("/var/run/xl2tpd/l2tp-control", "w")
        l2tp_file.write("c "+vpn_name)
        l2tp_file.close()

        if res.returncode ==0:
            return True
        else:
           return False
    except:
        return False

def disconnect_vpn(vpn_name):
    res = subprocess.run(["ipsec", "down", vpn_name])
    if res.returncode ==0:
        try:
            l2tp_file = open("/var/run/xl2tpd/l2tp-control", "w")
            l2tp_file.write("d "+vpn_name)
            l2tp_file.close()

            data = dict()
            ip, rx, tx = get_virtual_interface()
            data['connection_request'] == 'delete'
            data['network_id'] = ip + '_GATEWAY'

            send_to_query_server(data, server_addr, 3000)
            return True
        except:
            return False
    else:
        return False 
    

def query_vpn_network(params:dict):
    c_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    query_server_ip = "127.0.0.1"
    query_server_port = 1500
    c_sock.connect((query_server_ip, query_server_port))
    c_sock.send(json.dumps(params).encode("ascii"))
    data = c_sock.recv(1024)
    return json.loads(data)
    
def enable_port_forwarding(port, host_ip):
    gateway_ip = None
    subprocess.run(["chmod", "+x", root_path+"wifi_connect.sh"])
    res = subprocess.run([root_path+"wifi_connect.sh"], shell=True)

    if True:#res.returncode ==0:
        file = open(root_path+'logfiles/wlan_details.txt', 'r').readlines()
        for i in file:
            if 'inet ' in i:
                gateway_ip = i.split('inet ')[1].split(' netmask')[0] 


        try:
            file = open(root_path+"port_forwarding.sh","w")
            file.write("iptables -t nat -A PREROUTING -i ppp0 -p tcp --dport "+str(port)+" -j DNAT --to-destination "+host_ip+"\n")
            file.write("iptables -t nat -A POSTROUTING -o eth0 -p tcp --dport "+str(port)+" -d "+host_ip+" -j SNAT --to-source "+gateway_ip+"\n")
            file.close()

            res = subprocess.run(["chmod", "+x", root_path+"port_forwarding.sh"])
            res2 = subprocess.run(["bash", root_path+"port_forwarding.sh"])
            if res.returncode ==0 and res2.returncode ==0:
                db = sqlite3.connect(root_path+'gateway_stats.db')

                db.execute('INSERT INTO PORTS VALUES (?, ?)', (host_ip, port))
                db.commit()
                return True
            else:
                return False
            
        except:
            return False
    else:
        return False

