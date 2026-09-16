import socket
import threading

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
            send_message(address, goodbye_message.encode())
            c.close()
            break

        command = data.decode().split(" ")[0]
        if command == "/pm":
            to_user = data.decode().split(" ")[1]
            msg = data.decode().split(" ")[2:]
            if usernames_lookup.get(to_user) is None:
                c.sendall(f"WARNING: {to_user} doesn't exist.".encode())
            else:
                send_private_message(address, clients_lookup[usernames_lookup[to_user]], ' '.join(msg))
        else:
            send_message(address, data)

    
def send_message(from_address, msg):
    for client in clients_lookup:
        if client != from_address:
            clients_lookup[client].sendall(msg)

def send_private_message(from_address, to_socket, msg):
    to_socket.sendall(f"PRIVATE MESSAGE from {addresses_lookup[from_address]} : {msg}".encode())


while True:
    c, address = s.accept()
    data = c.recv(1024).decode().split(' ')
    name = data[0]
    if usernames_lookup.get(name) is None:
        addresses_lookup[address] = name
        clients_lookup[address] = c
        usernames_lookup[name] = address
        if len(address) > 1:
                send_message(address, " ".join(data).encode())
        thread1 = threading.Thread(target=get_message, args=(c,address), daemon= True)
        thread1.start()
    else:
        c.sendall("Somebody already has that name. You'll be disconnected.".encode())
        c.shutdown(socket.SHUT_WR)
        c.close()

# todo ftp