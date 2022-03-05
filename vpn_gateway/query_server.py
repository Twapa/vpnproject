import socket
import json

def vpn_listener():
    sock = socket.socket()
    print("Socket created ...")

    port = 1500
    sock.bind(('', port))
    sock.listen(5)

    print('socket is listening')

    while True:
        c, addr = sock.accept()
        print('got connection from ', addr)

        jsonReceived = json.loads(c.recv(1024).decode('ascii'))
        print("Json received -->", jsonReceived)

        c.close()