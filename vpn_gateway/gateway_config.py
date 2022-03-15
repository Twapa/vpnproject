'''
this script contains helper functions that will be used by
the GUI framework to make configuration changes on the router.
All functions will return True if they run successfully and return False otherwise
'''
import subprocess
import json
import socket

def initialise_vpn():
    #carries out necessary configurations prior to system startup
    res = subprocess.run(["/root/logfiles/init_connections.sh"], shell=True)
    
    if res.returncode ==0:
        return True
    else:
        return False

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

def change_dhcp_config():
    #changes settings in the dhcpcd.conf and dnsmasq.conf files
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

    try:
        l2tp_file = open("/var/run/xl2tpd/l2tp-control", "w")
        l2tp_file.write("d "+vpn_name)
        l2tp_file.close()

        if res.returncode ==0:
            return True
        else:
           return False 
    except:
        return False
    

def query_vpn_network(params:dict):
    c_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    query_server_ip = "127.0.0.1"
    query_server_port = 1500
    c_sock.connect((query_server_ip, query_server_port))
    c_sock.send(json.dumps(params).encode("ascii"))
    data = c_sock.recv(1024)
    return json.loads(data)
    