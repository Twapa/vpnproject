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

        if recieved_data['connection_request'] == 'create':     #determine if the gateway server wants to create or join a vpn network
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
                    server[13],          #cpu percent
                    server[14],          #ram percent
                    server[15],          #min rtt
                    server[16],          #avg rtt
                    server[17]           #max rtt
                    ])
            
            connection.sendall(json.dumps(access_servers).encode('ascii'))
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
                recieved_data["psk"])
            
            db = sqlite3.connect('vpn_servers.db')
            db.execute('INSERT INTO REGISTERED_NETWORKS VALUES (?, ?, ?, ?, ?)', values)
            db.commit()

            connection.close()

        elif recieved_data['connection_request'] == 'join':
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