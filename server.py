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

pubsub.subscribe('node_'+ port)

def get_message(c,address):
    while True:
        data = c.recv(1024)

        if c._closed or not data:
            goodbye_message = f"{addresses_lookup[address]} has left the chat"
            send_message(address, goodbye_message.encode())
            r.hdel('usernames', addresses_lookup[address])
            addresses_lookup.pop(address)
            clients_lookup.pop(address)
            c.close()
            break

        command = data.decode().split(" ")[0]
        if command == "/pm":
            target_user = data.decode().split(" ")[1]
            msg = data.decode().split(" ")[2:]
            if r.hget("usernames", target_user) is None:
                c.sendall(f"WARNING: {target_user} doesn't exist.".encode())
            else:
                target_port = r.hget("usernames", target_user)
                send_private_message(name, target_user, target_port, ' '.join(msg))
        else:
            send_message(address, data)

def get_redis_message():
    while True:
        for message in pubsub.listen():
            if message['type'] == 'message':
                if message['channel'].decode() == ('node_'+port):
                    from_user = message['data'].decode().split(":")[0]
                    to_user = message['data'].decode().split(":")[1]
                    message = message['data'].decode().split(":")[2]
                    clients_lookup[usernames_lookup[to_user]].sendall(f"PRIVATE MESSAGE from {str(from_user)} : {message}".encode())
                else:
                    print("SENDING IT TO EVERYBOdy")
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

def send_private_message(from_user, to_user, to_port, msg):
    channel = 'node_' + to_port.decode()
    r.publish(channel, f"{from_user}:{to_user}:{msg}")

thread2 = threading.Thread(target=get_redis_message, args=(), daemon= True)
thread2.start()

while True:
    c, address = s.accept()
    data = c.recv(1024).decode().split(' ')
    name = data[0]

    # if usernames_lookup.get(name) is None:
    if r.hget("usernames", name) is None or len(addresses_lookup) == 0:
        addresses_lookup[address] = name
        clients_lookup[address] = c
        usernames_lookup[name] = address
        r.hset("usernames", name, port)
        print(r.hgetall("usernames"))
        if len(address) > 1:
                send_message(address, " ".join(data).encode())
        thread1 = threading.Thread(target=get_message, args=(c,address), daemon= True)
        thread1.start()
    else:
        c.sendall("Somebody already has that name. You'll be disconnected.".encode())
        c.shutdown(socket.SHUT_WR)
        c.close()
