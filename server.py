import socket
import threading
import json

addresses_lookup = {}
clients_lookup = {}
usernames_lookup = {}

try:
    s = socket.socket()
    print("Socket is successfully created!")
except socket.error as e:
    print("Error creating socket: ", e)

port = 8080
s.bind(('', port))
s.listen(5)

def get_message(c,address):
    while True:
        print("<><><><><", c._closed)
        if c._closed:
            break
        
        data = c.recv(1024)

        if not data:
            break
        send_message(c, address, data)

    
    # addresses.pop(address)
    # clients.pop(c)
    # c.close()
    # print({'addresses':addresses, 'clients':clients})
    



def send_message(c, from_address, msg):
    for client in clients_lookup:
        if client != from_address:
            clients_lookup[client].sendall(msg)


while True:
    c, address = s.accept()
    print("BEFORE IF/ELSE BLOCK", addresses_lookup)
    name = c.recv(1024).decode().split(' ')[0]
    if usernames_lookup.get(name) is None:
        addresses_lookup[address] = name
        clients_lookup[address] = c
        usernames_lookup[name] = address
    else:
        c.close()

    # print("AFTER IF/ELSE BLOCK", addresses_lookup)
    thread1 = threading.Thread(target=get_message, args=(c,address), daemon= True)
    thread1.start()