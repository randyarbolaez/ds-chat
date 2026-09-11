import socket
import threading

addresses = {}
clients = {}

try:
    s = socket.socket()
    print("Socket is successfully created!")
except socket.error as e:
    print("Error creating socket: ", e)

port = 8080
s.bind(('', port))
s.listen(5)

def get_message(c,address):
    print(f"Connection from {address}")
    while True:
        data = c.recv(1024)

        if not data:
            break
        # blah = {f"{addresses[address]}":data.decode()}
        # print({blah})
        send_message(c, address, data)



def send_message(c, from_address, msg):
    for client in clients:
        if client != from_address:
            clients[client].sendall(msg)


while True:
    c, address = s.accept()
    addresses[address] = c.recv(1024).decode().split(' ')[0]
    clients[address] = c

    print(addresses)
    thread1 = threading.Thread(target=get_message, args=(c,address), daemon= True)
    thread1.start()