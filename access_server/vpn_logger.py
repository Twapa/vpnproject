'''
THIS SCRIPT SHOULD BE HOSTED ON THE VPN SERVER SCRIPT FOR STRONGSWAN
.....................................................................
The script will extract vpn statistics on the VPN server
'''
import subprocess
import time
import socket
import sys
import json
import psutil
import threading
import platform
import requests

# program that executes a bash script that logs
# the current state of VPN connections every one minute
def log_connections(_seconds):
    :param name: _seconds -m Seconds to sleep between
    while True:
        subprocess.run(["logtraffic.sh"], shell=True)
        time.sleep(_seconds)

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

def process_text():                 #extras status infomation from text files
    clients = []
    res = dict()
    try:
        trafficstatus_file = open('trafficstatus.txt', 'r').readlines()
        for i in trafficstatus_file:
            client = []
            temp = i.split(' ')[2].split('[')[0]                           #connection protocol
            client.append(temp[1:len(temp)-1])
            client.append(i.split(']')[1].split(',')[0])                   #ip address
            client.append(i.split('type=')[1].split(',')[0])               #connection type
            client.append(i.split('add_time=')[1].split(',')[0])           #add time
            client.append(i.split('inBytes=')[1].split(',')[0])            #bytes sent to the server
            client.append(i.split('outBytes=')[1].split(',')[0])           #bytes sent from server
            temp = i.split('id=')[1].split(',')[0]                         #client ip address
            client.append(temp[1:len(temp)-2])

            clients.append(client)
        res['clients'] = clients

        briefstatus_file = open('status.txt', 'r').readlines()

        #IPsec security associations
        briefstatus_file[2]
        res['ipsec_total_users'] = int(briefstatus_file[2].split('total')[1][1])
        res['ipsec_authenticated_users'] = int(briefstatus_file[2].split('authenticated')[1][1])
        res['ipsec_anonymous_users'] = int(briefstatus_file[2].split('anonymous')[1][1])

        #IKEv2 security associations
        briefstatus_file[1]
        res['ikev2_total_certs'] = int(briefstatus_file[1].split('total')[1][1])
        res['ike_half_open_certs'] = int(briefstatus_file[1].split('half-open')[1][1])
        res['ikev2_open_conn'] = int(briefstatus_file[1].split('open')[2][1])
        res['ikev2_authenticated_users'] = int(briefstatus_file[1].split('authenticated')[1][1])
        res['ikev2_anonymous_users'] = int(briefstatus_file[1].split('anonymous')[1][1])

        return res
    except:
        return False

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

    network = {"traffic_in" : current_in, "traffic_out" : current_out}
    return network 

def get_cpu_ram_usage(_time_interval):      #returns cpu and ram usage
    cpu_percent = psutil.cpu_percent(_time_interval)    #measured over a specific time interval
    ram_percent = psutil.virtual_memory()[2]
    usage = {"cpu_percent":cpu_percent, "ram_percent":ram_percent}
    return usage

def measure_latency():
    # this function attempts to measure minimum, average and maximum 
    # round trip time (rtt) by pinging any of the vpn client ips

    # implement a method of finding out one of the client's virtual ip to ping with
    # the ip provided is just an example ip used to test the functionality of the function

    #ip_address = '216.58.223.132'           #google.com's ip address
    #p = subprocess.Popen(["ping","-c","4",ip_address], stdout = subprocess.PIPE)
    #res = p.communicate()[0].decode('ascii')
    #values = res.split('mdev')[1].split('/')
    #min_rtt = float(values[0].split('=')[1])
    #avg_rtt = float(values[1])
    #max_rtt = float(values[2])

    #return {"min_rtt":min_rtt,"avg_rtt":avg_rtt,"max_rtt":max_rtt}
    return {"min_rtt":6.34,"avg_rtt":7.63,"max_rtt":12.345}

def send_statistics(time_interval, server_addr, port):
    time_interval = 60
    while True:
        #get all server stats
        usage = get_cpu_ram_usage(5)
        bandwidth = get_bandwidth()
        net_stats = measure_latency()
        data = process_text()
        #data.update({"hostname":platform.node()})
        data.update({"time_submitted":int(time.time())})
        data.update(usage)
        data.update(bandwidth)
        data.update(net_stats)
        data.update(requests.get('http://ipinfo.io/json').json())       #gets the location of the server

        #send to query server
        send_to_query_server(data, server_addr, port)
        time.sleep(time_interval)
        

def run():
    query_server_ip = input('Enter query servery IP address   : ')
    query_server_port = input('Enter query servery IP port     : ')
    time_interval = input('Send statistics after (seconds) : ')

    t1 = threading.Thread(target=log_connections, args=(time_interval,), daemon=True)
    t2 = threading.Thread(target=send_statistics, args=(time_interval,query_server_ip,query_server_port), daemon=True)
    t1.start() 
    t2.start()




