import paramiko

import re
import json

def convert(a):
    # it = iter(a)
    # res = dict(zip(it, it))
    # return res
    res ={a[i]: a[i] for i in range(0,len(a),2)}
    return res

def serverstatus():
    paramiko.util.log_to_file("paramiko2.log")
    # initialize the SSH client
    client = paramiko.SSHClient()
    # add to known hosts
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect('45.79.122.105', username='root', password='twapalisha')
    except:
        print("[!] Cannot connect to the SSH Server")
        exit()



    
    ipregex = r'\.(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'

    stdin, stdout, stderr = client.exec_command('ipsec statusall')
    
    list = stdout.readlines()
    
    output = [line.rstrip() for line in list]
    
    outputstr =''.join(output)
    iplist = re.findall(ipregex,outputstr)
    ipmap = convert(iplist)
    jsonmap = json.dumps(ipmap)
    
    
    err = stderr.read().decode()
    if err:
        client.close()
        print('read error')            

    client.close()
    

    return jsonmap

def save_file():
    status_api = serverstatus()
    print(status_api)
    with open('data.json','w') as fd:
        
        fd.write(status_api)


if __name__ == '__main__':
    save_file()            