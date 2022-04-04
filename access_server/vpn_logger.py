'''
THIS SCRIPT SHOULD BE HOSTED ON THE VPN SERVER
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
import sqlite3

# program that executes a bash script that logs
# the current state of VPN connections every one minute
def log_connections(_seconds):
    while True:
        subprocess.run(["./logtraffic.sh"], shell=True)
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

        netstat = open('netstat.txt', 'r').readlines()
        netstat_data = netstat.readlines()
        for text in netstat_data:
            if 'dropped' in text:
                res['dropped_packets'] = int(text.split('dropped')[0])
            else:
                res['dropped_packets'] = 0
            
            if 'total packets received' in text:
                res['total_packets_received'] = int(text.split('total')[0])

        states_file = open('states.txt', 'r').readlines()
        ip_port, traffic_data = [], []
        for item in states_file:
            if 'IPsec SA established' in item:
                ip_port.append(item.split(']')[1].split(' ')[1])        #ip address and port
            if 'Traffic' in item:
                traffic_data.append(
                    [item.split(']')[1].split('Traffic')[1].split('ESPin=')[1].split(' ')[0],     #traffic in
                    item.split(']')[1].split('Traffic')[1].split('ESPout=')[1].split(' ')[0]]     #traffic out
                )
        
        _clients = []
        if len(ip_port) > 0:
            for i in range(0, len(ip_port)):
                _clients.append([ip_port[i], traffic_data[i][0], traffic_data[i][1]])
        res['client_states'] = _clients

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

    ip_address = '216.58.223.132'           #google.com's ip address
    p = subprocess.Popen(["ping","-c","4",ip_address], stdout = subprocess.PIPE)
    res = p.communicate()[0].decode('ascii')
    values = res.split('mdev')[1].split('/')
    min_rtt = float(values[0].split('=')[1])
    avg_rtt = float(values[1])
    max_rtt = float(values[2])

    return {"min_rtt":min_rtt,"avg_rtt":avg_rtt,"max_rtt":max_rtt}
    #return {"min_rtt":6.34,"avg_rtt":7.63,"max_rtt":12.345}

def send_statistics(time_interval, server_addr, port):
    #time_interval = 60
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
        data.update({"datatype":'linux'})

        chap_secrets_file = open('/etc/ppp/chap-secrets', 'r')
        data.update({"chap_secrets": chap_secrets_file.readlines()})
        chap_secrets_file.close()

        psk_secret_file = open('/etc/ipsec.secrets', 'r') 
        data.update({"psk":psk_secret_file.readlines()[0].split('PSK')[1].split("\"")[1]})
        psk_secret_file.close()

        #send to query server
        send_to_query_server(data, server_addr, port)
        time.sleep(time_interval)
        
def vpn_listener():
    sock = socket.socket()
    print("Socket VPN access servers created ...")

    port = 1777
    sock.bind(('', port))
    sock.listen(1)

    print('socket is listening')

    while True:
        connection, addr = sock.accept()
        print('got connection from ', addr)

        recieved_data = json.loads(connection.recv(1024).decode('ascii'))
        print("Json received -->", recieved_data)

        db = sqlite3.connect('/root/vpn_server/vpn_servers.db')

        #Managing VPN Users
        if recieved_data['action'] == 'add_user':
            user_file = open('/etc/ppp/chap-secrets', 'a')
            user_file.write('\n\"'+recieved_data['username']+'\" l2tpd \"'+recieved_data['password']+'\" *') 
            user_file.close()

        elif recieved_data['action'] == 'delete_user':
            user_file = open('/etc/ppp/chap-secrets', 'r')
            user_list = user_file.readlines()
            if len(user_list) > 0:
                for _user in user_list:
                    if recieved_data['username'] in _user:
                        user_list.remove(_user)
                        user_file.close()

                user_file = open('/etc/ppp/chap-secrets', 'w')
                for _user in user_list:
                    user_file.write(_user)
                user_file.close()

        elif recieved_data['action'] == 'change_user':
            user_file = open('/etc/ppp/chap-secrets', 'r')
            user_list = user_file.readlines()
            if len(user_list) > 0:
                for _user in user_list:
                    if recieved_data['username'] in _user:
                        user_list.remove(_user)
                        user_file.close()

                user_file = open('/etc/ppp/chap-secrets', 'w')
                for _user in user_list:
                    user_file.write(_user)
                user_file.close()

            user_file = open('/etc/ppp/chap-secrets', 'a')
            user_file.write('\n\"'+recieved_data['username']+'\" l2tpd \"'+recieved_data['password']+'\" *') 
            user_file.close()

        elif recieved_data['action'] == 'change_psk':
            psk_secret_file = open('/etc/ipsec.secrets', 'w')
            psk_secret_file.write('%any  %any  : PSK \"'+recieved_data['psk']+'\"')
            psk_secret_file.close()

            res1 = subprocess.run(["service", "ipsec", "restart"])
            res2 = subprocess.run(["service", "xl2tpd", "restart"])
            if res1.returncode ==0 and res2.returncode ==0:
                pass

        # Network Configuration
        elif recieved_data['action'] == 'assign_static_ip':             #assigns a static ip address to a specific vpn user 
            user_file = open('/etc/ppp/chap-secrets', 'r')
            user_list = user_file.readlines()
            if len(user_list) > 0:
                for _user in user_list:
                    if recieved_data['username'] in _user:
                        user_list.remove(_user)
                        user_file.close()

                user_file = open('/etc/ppp/chap-secrets', 'w')
                for _user in user_list:
                    user_file.write(_user)
                user_file.close()

            user_file = open('/etc/ppp/chap-secrets', 'a')
            user_file.write('\n\"'+recieved_data['username']+'\" l2tpd \"'+recieved_data['password']+'\" '+recieved_data['ip_address']) 
            user_file.close()

        elif recieved_data['action'] == 'enable_port_forward':
            try:
                file = open("/root/vpn_server/port_forwarding.sh","w")
                file.write("iiptables -I FORWARD 2 -i eth0 -o ppp+ -p tcp --dport "+recieved_data['port']+" -j ACCEPT\n")
                file.write("iptables -t nat -A PREROUTING -p tcp --dport "+recieved_data['port']+" -j DNAT --to "+recieved_data['ip_address']+"\n")
                file.close()


                db.execute('INSERT INTO PORTS(port_number, client_ip) VALUES (?,?)', (recieved_data['port'], recieved_data['ip_address']))
                db.commit()

                res = subprocess.run(["chmod", "+x", "/root/vpn_server/port_forwarding.sh"])
                res2 = subprocess.run(["bash", "/root/vpn_server/port_forwarding.sh"])
                if res.returncode ==0 and res2.returncode ==0:
                    pass
            except:
                pass
        
        elif recieved_data['action'] == 'disable_port_forward':
            try:
                file = open("/root/vpn_server/port_forwarding.sh","w")
                file.write("iiptables -D FORWARD 2 -i eth0 -o ppp+ -p tcp --dport "+recieved_data['port']+" -j ACCEPT\n")
                file.write("iptables -t nat -D PREROUTING -p tcp --dport "+recieved_data['port']+" -j DNAT --to "+recieved_data['ip_address']+"\n")
                file.close()

                db.execute('DELETE FROM PORTS WHERE port_number=?',(recieved_data['port'],))
                db.commit()

                res = subprocess.run(["chmod", "+x", "/root/vpn_server/port_forwarding.sh"])
                res2 = subprocess.run(["bash", "/root/vpn_server/port_forwarding.sh"])
                if res.returncode ==0 and res2.returncode ==0:
                    pass
            except:
                pass

def run():
    query_server_ip = input('Enter query servery IP address   : ')
    query_server_port = int(input('Enter query servery IP port     : '))
    time_interval = int(input('Send statistics after (seconds) : '))

    thread_list = []
    t1 = threading.Thread(target=log_connections, args=(time_interval,), daemon=True)
    t2 = threading.Thread(target=send_statistics, args=(time_interval,query_server_ip,query_server_port), daemon=True)
    thread_list.append(t1)
    thread_list.append(t2)
    t1.start() 
    t2.start()

    while True:
        for _thread in thread_list:
            if _thread.is_alive() == False:
                sys.exit()

        time.sleep(10)

if __name__ == '__main__':
    run()