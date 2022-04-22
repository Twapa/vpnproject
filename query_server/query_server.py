import socket
import json
import threading
import sqlite3
import sys
import time

#this function is used to listen for connections coming from vpn access servers
def vpn_listener():
    sock = socket.socket()
    print("Socket VPN access servers created ...")

    port = 1500
    sock.bind(('', port))
    sock.listen(5)

    print('socket is listening')

    while True:
        connection, addr = sock.accept()
        print('got connection from ', addr)

<<<<<<< HEAD
        
        
        recieved_data = json.loads(connection.recv(1024).decode('ascii'))
        # recieved_data = connection.recv(1024)

        print("Json received -->", recieved_data)
        
        #write in database vpn access server statistics
        #store in database
        # db = sqlite3.connect('vpn_servers.db')
        # values = (
        #     recieved_data['time_submitted'],
        #     recieved_data['hostname'],
        #     recieved_data['country'],
        #     recieved_data['ipsec_total_users'],
        #     recieved_data['ipsec_authenticated_users'],
        #     recieved_data['ipsec_anonymous_users'],
        #     recieved_data['ikev2_total_certs'],
        #     recieved_data['ike_half_open_certs'],
        #     recieved_data['ikev2_open_conn'],
        #     recieved_data['ikev2_authenticated_users'],
        #     recieved_data['ikev2_anonymous_users'],
        #     recieved_data['traffic_in'],
        #     recieved_data['traffic_out'],
        #     recieved_data['cpu_percent'],
        #     recieved_data['ram_percent'],
        #     recieved_data['min_rtt'],
        #     recieved_data['avg_rtt'],
        #     recieved_data['max_rtt'])
        
        # db.execute('INSERT INTO ACCESS_SERVER_STATISTICS(time_submitted,' +\
        #     'hostname, country, ipsec_total_users, ipsec_authenticated_users,' +\
        #     'ipsec_anonymous_users, ikev2_total_certs, ike_half_open_certs, ikev2_open_conn,' +\
        #     'ikev2_authenticated_users, ikev2_anonymous_users, traffic_in, traffic_out,' +\
        #     'cpu_percent, ram_percent, min_rtt, avg_rtt, max_rtt) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
        #     values)
        # db.commit()

        # connection.close()
=======
        recieved_data = json.loads(connection.recv(7024).decode('ascii'))
        
        
        #write in database vpn access server statistics
        #store in database
        db = sqlite3.connect('vpn_servers.db')

        if recieved_data['datatype'] == 'android':
            print("Android Json received -->", recieved_data)
            if len(recieved_data['clienteap']) > 0:
                for _client in recieved_data['clienteap']:
                    values=(
                        recieved_data['hostname'],
                        recieved_data['ip'],
                        _client[0],
                        _client[1],
                        _client[2],
                        _client[3],
                        _client[4],
                        _client[5],
                        _client[6],
                    )
                    db.execute('INSERT INTO EAP_CLIENTS(hostname, ip_address, username, password, server_ip, encryption_type, bytes_in, bytes_out, client_ip)' +\
                        'VALUES (?,?,?,?,?,?,?,?,?)', values)

            values = (
                recieved_data['time_submitted'],
                recieved_data['hostname'],
                recieved_data['country'],
                len(recieved_data['clienteap']),
                len(recieved_data['clienteap']),
                0,
                0,
                0,
                0,
                0,
                0,
                recieved_data['traffic_in'],
                recieved_data['traffic_out'],
                recieved_data['cpu_percent'],
                recieved_data['ram_percent'],
                recieved_data['min_rtt'],
                recieved_data['avg_rtt'],
                recieved_data['max_rtt'],
                recieved_data['ip'],
                recieved_data['total_packets_received'],
                recieved_data['dropped_packets'],
                )
            
            db.execute('INSERT INTO ACCESS_SERVER_STATISTICS(time_submitted,' +\
                'hostname, country, ipsec_total_users, ipsec_authenticated_users,' +\
                'ipsec_anonymous_users, ikev2_total_certs, ike_half_open_certs, ikev2_open_conn,' +\
                'ikev2_authenticated_users, ikev2_anonymous_users, traffic_in, traffic_out,' +\
                'cpu_percent, ram_percent, min_rtt, avg_rtt, max_rtt, ip_address, total_packets_received,' +\
                'dropped_packets) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', values)

            db.commit()
            connection.close()

        elif recieved_data['datatype'] == 'linux':
            print("Linux Json received -->", recieved_data)
            values = (
                recieved_data['time_submitted'],
                recieved_data['hostname'],
                recieved_data['country'],
                recieved_data['ipsec_total_users'],
                recieved_data['ipsec_authenticated_users'],
                recieved_data['ipsec_anonymous_users'],
                recieved_data['ikev2_total_certs'],
                recieved_data['ike_half_open_certs'],
                recieved_data['ikev2_open_conn'],
                recieved_data['ikev2_authenticated_users'],
                recieved_data['ikev2_anonymous_users'],
                recieved_data['traffic_in'],
                recieved_data['traffic_out'],
                recieved_data['cpu_percent'],
                recieved_data['ram_percent'],
                recieved_data['min_rtt'],
                recieved_data['avg_rtt'],
                recieved_data['max_rtt'],
                recieved_data['ip'],
                recieved_data['total_packets_received'],
                recieved_data['dropped_packets'],
                recieved_data['ipsec_status']
                )
            
            db.execute('INSERT INTO ACCESS_SERVER_STATISTICS(time_submitted,' +\
                'hostname, country, ipsec_total_users, ipsec_authenticated_users,' +\
                'ipsec_anonymous_users, ikev2_total_certs, ike_half_open_certs, ikev2_open_conn,' +\
                'ikev2_authenticated_users, ikev2_anonymous_users, traffic_in, traffic_out,' +\
                'cpu_percent, ram_percent, min_rtt, avg_rtt, max_rtt, ip_address, total_packets_received,' +\
                'dropped_packets, ipsec_status) VALUES (?, ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', values)
            
            recieved_data['ports'][0]
            recieved_data['ports'][1]

            if len(recieved_data['ports'][1]) > 0:
                db.execute('DROP TABLE IF EXISTS PORTS')
                db.execute('CREATE TABLE PORTS (hostname TEXT, ip_address TEXT, port INTEGER, client_ip	TEXT)')
                #db.execute('create table iceberg_parts(symbol text, limits REAL)')
                for i in range(0, len(recieved_data['ports'][0])):
                    values = (
                        recieved_data['hostname'],
                        recieved_data['ip'],
                        recieved_data['ports'][0][i],
                        recieved_data['ports'][1][i],
                        recieved_data['ports'][2][i]
                    )
                    
                    db.execute('INSERT INTO PORTS(hostname, ip_address, port, client_ip, status) VALUES (?,?,?,?,?)', values)

            for item in recieved_data['chap_secrets']:
                values =(
                    recieved_data['hostname'],
                    item.split('\n')[0].split('\"')[4],
                    item.split('\n')[0].split('\"')[1],
                    item.split('\n')[0].split('\"')[3],
                    recieved_data['psk']
                )
                db.execute('INSERT INTO CHAP_SECRETS(hostname, ip_address, username, password, psk) VALUES (?,?,?,?,?)', values)

            if len(recieved_data['client_states']) > 0:
               
                for item in recieved_data['client_states']:
                    values =(
                        recieved_data['hostname'],
                        item[0],
                        item[1],
                        item[2],
                    )
                    db.execute('INSERT INTO CLIENT_STATES(hostname, ip_port, traffic_in, traffic_out) VALUES (?,?,?,?)', values)

            db.commit()
            connection.close()
>>>>>>> d59373037cef09097def13ff6015e8d632ac830a

def gateway_listener():     #this method is used to listen for connections comming from gateway routers
    sock = socket.socket()
    print("Socket for gateway routers created ...")

    port = 3000
    sock.bind(('', port))
    sock.listen(5)

    print('socket is listening')

    while True:
        connection, address = sock.accept()  # accept an incoming connection
        
        recieved_data = json.loads(connection.recv(1024).decode('ascii'))
        print("Json received -->", recieved_data)

        if recieved_data['connection_request'] == 'query_servers':     #determine if the gateway server wants to create or join a vpn network
            #search in database for available access servers
            _servers, access_servers = [], []
            temp, temp2, temp3 = [], [], []
            #temp = None
            db = sqlite3.connect('vpn_servers.db')
            db.row_factory = sqlite3.Row
            cursor = db.execute('SELECT * FROM ACCESS_SERVER_STATISTICS')
            for row in cursor:
                temp.append(row)
            if len(temp) != 0:
                for i in temp:
                    temp2.append(i[1])      #collect a list of host names
                temp2 = list(set(temp2))
                for _name in temp2:
                    cursor = db.execute('SELECT * FROM ACCESS_SERVER_STATISTICS WHERE hostname =?',(_name,))
                    for row in cursor:
                        temp3.append(row)
                    _servers.append(temp3[len(temp3)-1])

            for server in _servers:
                    access_servers.append([
                    server[1],           #hostname
                    server[2],           #location
                    server[3],           #total users
                    server[13],          #cpu percent
                    server[14],          #ram percent
                    server[15],          #min rtt
                    server[16],          #avg rtt
                    server[17],          #max rtt
                    server[18],          #ip address
                    server[21]           #ipsec status
                    ])
            
            resf = []
            for i in  access_servers:
                res = []
                cursor = db.execute('SELECT * FROM CHAP_SECRETS WHERE hostname=?',(i[0],))
                for row in cursor:
                    res.append(row[0]+'$$$'+row[2]+'$$$'+row[3]+'$$$'+row[4]+'$$$'+i[1]+'$$$'+str(i[2])+'$$$'+str(i[7])+'$$$'+i[8])

                resf.append(list(set(res)))
                    

            connection.sendall(json.dumps(resf).encode('ascii'))
            print('RETURNED : ',access_servers)
            #registered_network_data = json.loads(connection.recv(1024).decode('ascii'))

            connection.close()

        elif recieved_data['connection_request'] == 'delete':
            db = sqlite3.connect('vpn_servers.db')
            db.execute('DELETE FROM REGISTERED_NETWORKS WHERE network_id=?',(recieved_data["network_id"],))
            db.commit()

            connection.close()

        elif recieved_data['connection_request'] == 'register':
            #registered_network_data = json.loads(connection.recv(1024).decode('ascii'))
            values = (
                recieved_data["network_id"],
                recieved_data["server_ip"],
                recieved_data["username"],
                recieved_data["password"],
                recieved_data["psk"],
                recieved_data["router_ip"])
            
            db = sqlite3.connect('vpn_servers.db')
            db.execute('INSERT INTO REGISTERED_NETWORKS VALUES (?, ?, ?, ?, ?)', values)
            db.commit()

            connection.close()

        elif recieved_data['connection_request'] == 'join_request':
            #search in database for access servers based on vpn id
            db = sqlite3.connect('vpn_servers.db')
            db.row_factory = sqlite3.Row
            cursor = db.execute('SELECT * FROM REGISTERED_NETWORKS WHERE network_id=?',(recieved_data["network_id"],))
            for row in cursor:
                connection.sendall(json.dumps(dict(row)).encode('ascii'))
            
            #connection.sendall(json.dumps(data).encode('ascii'))
            connection.close()


if __name__ == '__main__':
    thread_list = []
    # t1 = threading.Thread(target=gateway_listener, daemon=True)
    t2 = threading.Thread(target=vpn_listener, daemon=True)
    # thread_list.append(t1)
    thread_list.append(t2)
    # t1.start()
    t2.start()

    while True:
        for _thread in thread_list:
            if _thread.is_alive() == False:
                sys.exit()

        time.sleep(10)



'''
#example of returned data
            access_servers = {
                "servers":[
                    {"virmach_ny":[     #server name
                        "new york",     #location
                        2,              #active users
                        10.3458,        #min rtt
                        7.4095,         #avg rtt
                        122.459         #max rtt
                        ]
                    },
                    {"linode_dehli":[     
                        "Dehli",     
                        15,              
                        150,
                        34,
                        5.344             
                        ]
                    }
                ]
            }


            #example of returned data
            data = {
                "server":[
                    {"linode_dehli":[     
                        "active",       
                        "Dehli",     
                        15,              
                        150             
                        ]
                    }
                ],
                "ip":"107.172.197.127",
                "username":"dehli_user1",
                "password":"dehli_1234",
                "psk":"obyb23787f2fyewfoiaf",
                "type":"l2tp"
            }
'''

