import subprocess
import time
import socket
import sys
import json
import psutil


# program that executes a bash script that logs
# the current state of VPN connections every one minute
def log_connections(_seconds):
    while True:
        subprocess.run(["/root/logfiles/logtraffic.sh"], shell=True)
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
    except socket.gaierror:
        print('There an error resolving the host')

def process_text():                 #extras status infomation from text files
    clients = []
    res = dict()
    try:
        trafficstatus_file = open('/root/logfiles/trafficstatus.txt', 'r').readlines()
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

        briefstatus_file = open('/root/logfiles/status.txt', 'r').readlines()

        #IPsec security associations
        briefstatus_file[2]
        res['ipsec_total_users'] = int(briefstatus_file[2].split('total')[1][1])
        res['ipsec_authenticated_users'] = int(briefstatus_file[2].split('authenticated')[1][1])
        res['ipsec_anonymous_users'] = int(briefstatus_file[2].split('anonymous')[1][1])

        #IKEv2 security associations
        briefstatus_file[1]
        res['total_certs'] = int(briefstatus_file[1].split('total')[1][1])
        res['half_open_certs'] = int(briefstatus_file[1].split('half-open')[1][1])
        res['ikev2_open_conn'] = int(briefstatus_file[1].split('open')[2][1])
        res['ike_authenticated_users'] = int(briefstatus_file[1].split('authenticated')[1][1])
        res['ike_anonymous_users'] = int(briefstatus_file[1].split('anonymous')[1][1])

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
    return cpu_percent, ram_percent