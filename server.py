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
        data = c.recv(1024)

        if c._closed or not data:
            goodbye_message = f"{addresses_lookup[address]} has left the chat"
            print(goodbye_message)
            usernames_lookup.pop(addresses_lookup[address])
            addresses_lookup.pop(address)
            clients_lookup.pop(address)
            send_message(c, address, goodbye_message.encode())
            c.close()
            print({'addresses':addresses_lookup, 'clients':clients_lookup, 'usernames': usernames_lookup})
            break

        # if not data:
        #     print("NOT DATA ?")
        #     break
        # print("data <><><><>")
        send_message(c, address, data)
    



def send_message(c, from_address, msg):
    for client in clients_lookup:
        if client != from_address:
            clients_lookup[client].sendall(msg)


while True:
    c, address = s.accept()
    print("BEFORE IF/ELSE BLOCK", addresses_lookup)
    data = c.recv(1024).decode().split(' ')
    name = data[0]
    if usernames_lookup.get(name) is None:
        addresses_lookup[address] = name
        clients_lookup[address] = c
        usernames_lookup[name] = address
    else:
        c.close()
    if len(address) > 1:
        send_message(c, address, " ".join(data).encode())

    # print("AFTER IF/ELSE BLOCK", addresses_lookup)
    thread1 = threading.Thread(target=get_message, args=(c,address), daemon= True)
    thread1.start()