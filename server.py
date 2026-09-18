import socket
import threading
import redis
from dotenv import load_dotenv
import os
import sys

addresses_lookup = {}
clients_lookup = {}
usernames_lookup = {}

load_dotenv()  

redis_url = os.getenv("REDIS_URL")

r = redis.Redis.from_url(redis_url)

pubsub = r.pubsub()

pubsub.subscribe('global_chat')

try:
    s = socket.socket()
    print("Socket is successfully created!")
except socket.error as e:
    print("Error creating socket: ", e)

port = sys.argv[1]
print("port <> ", port)
s.bind(('', int(port)))
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

def get_redis_message():
    for message in pubsub.listen():
        if message['type'] == 'message':
            print(f"Data:{message['data']}")
            from_username = message['data'].decode().split()[0].split(":")[0]

            for client in list(clients_lookup.keys()):
                local_username = addresses_lookup.get(client)
                if local_username == from_username:
                    continue
                else:
                    clients_lookup[client].sendall(message['data'])

    
def send_message(from_address, msg):
    username = addresses_lookup[from_address]
    actual_message = f"{username}:{msg}"
    r.publish('global_chat', actual_message) 

def send_private_message(from_address, to_socket, msg):
    to_socket.sendall(f"PRIVATE MESSAGE from {addresses_lookup[from_address]} : {msg}".encode())

thread2 = threading.Thread(target=get_redis_message, args=(), daemon= True)
thread2.start()

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

# todo clean up
# /pm

# todo ftp