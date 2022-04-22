'''
THIS SCRIPT SHOULD BE HOSTED ON THE LINUX VPN SERVER
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
import re

# program that executes a bash script that logs
# the current state of VPN connections every one minute
def log_connections(_seconds):
    while True:
        subprocess.run(["logtraffic.sh"], shell=True)
        time.sleep(_seconds)


# regular expression method to find string between specified words
def find_between(s, first, last):
    try:
        regex = rf'{first}(.*?){last}'
        return re.findall(regex, s)
    except ValueError:
        return -1
#method creates socket and sends json object 
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

def find_between(s, first, last):
        try:
            regex = rf'{first}(.*?){last}'
            return re.findall(regex, s)
        except ValueError:
            return -1

# method retrieves information on server
def process_text(username, password):

    trafficstatus_file = open('/logfiles/trafficstatus.txt', 'r').readlines() 
    output = [list.rstrip() for list in trafficstatus_file]
    resp =''.join(output)

    clients = []
    res = dict()

    ipregexp = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\[\d'
    ipcregexp = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'

    res = dict()
    found_values = find_between(resp,"ESTABLISHED", "/32")

    clients = []
    for i in found_values:
        
        client = []
        
        temp = i.split(',')
        
        # conectedtime = temp[0]
        client.append(username)
        client.append(password)
        server = temp[1]
        serverip = re.findall(ipregexp,server) # extract ipaddress
        ip = ''.join(serverip)
        client.append(ip)
        
        
        ikeused = temp[2] # extract IKE agorithm used
        ikelist = find_between(ikeused,'proposal:','roadwarrior')
        ike = ''.join(ikelist)
        client.append(ike)
        
        
        
        packetsin = temp[6]# extact packets received by vpn server
        pacin = find_between(packetsin,' ','bytes')
        pin =''.join(pacin)
        client.append(pin)
        
        packetsout =temp[8] # extact packets sent by  by vpn server
        pacout = find_between(packetsout,' ','bytes')
        pout = ''.join(pacout)
        client.append(pout)
        
        clientip = temp[10] #extact clients ip_address connected
        clientipreg =re.findall(ipcregexp,clientip)

        client.append(clientipreg[1])
        
        clients.append(client)


    numberclient = len(clients)
    clients.append(numberclient)
    res["clienteap"] = clients   
    res["numberclients"] = numberclient 

              

    return res  


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

    ip_address = '216.58.223.132'           #google.com's ip address
    p = subprocess.Popen(["ping","-c","4",ip_address], stdout = subprocess.PIPE)
    res = p.communicate()[0].decode('ascii')
    values = res.split('mdev')[1].split('/')
    min_rtt = float(values[0].split('=')[1])
    avg_rtt = float(values[1])
    max_rtt = float(values[2])





def send_statistics(time_interval , server_addr, port,username,password):
    time_interval = 60
    while True:
        #get all server stats
        # usage = get_cpu_ram_usage(5)
        # bandwidth = get_bandwidth()
        # net_stats = measure_latency()
        data = process_text(username,password)
        #data.update({"hostname":platform.node()})

        data.update({"time_submitted":int(time.time())})
        # data.update(usage)
        # data.update(bandwidth)
        # data.update(net_stats)
        data.update(requests.get('http://ipinfo.io/json').json())       #gets the location of the server
        data.update({'datatype':'android'})
        #send to query server
        # send_to_query_server(data, server_addr, port)
        print(data)
        time.sleep(time_interval)    


def run():
    thread_list = []
    query_server_ip = input('Enter query servery IP address   : ')
    query_server_port = int(input('Enter query servery IP port     : '))
    time_interval = int(input('Send statistics after (seconds) : '))
    vpnusername = input('Enter vpn username address   : ')
    vpnpassword = input('Enter vpn password address   : ')

    # t1 = threading.Thread(target=log_connections, args=(time_interval,), daemon=True)
    t2 = threading.Thread(target=send_statistics, args=(time_interval,query_server_ip,query_server_port,vpnusername, vpnpassword), daemon=True)
    # t1.start() 
    t2.start()
    # thread_list.append(t1) 
    thread_list.append(t2)
    while True:

        for _thread in thread_list:
            if _thread.is_alive == False:
                sys.exit() 

            time.sleep(10)    

    
if __name__ == '__main__':
    run()









