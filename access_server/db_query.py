import sqlite3

def get_open_port(root_path):
    ports = []
    client_ip= []
    status = []
    db = sqlite3.connect(root_path+'server_data.db')
    db.row_factory = sqlite3.Row
    cursor = db.execute('SELECT * FROM PORTS')
    for row in cursor:
        ports.append(row[0])
        client_ip.append(row[1])
        status.append(row[2])

    return {'ports':[ports,client_ip]}