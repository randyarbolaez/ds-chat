import socket
import threading
import os
import sys
import redis
from dotenv import load_dotenv

load_dotenv()

redis_url = os.getenv("REDIS_URL")

r = redis.Redis.from_url(redis_url)

s = socket.socket()

port = sys.argv[1]

s.connect(('127.0.0.1', int(port)))

name = input("What is your name? ")
s.send(f"{name} has joined the chat".encode())

def find_port():
    every_port = r.hgetall("ports")
    min_connection = 0
    min_connection_port = 0
    for port, connections in every_port.items():
        if int(connections) > 0:
            if min_connection == 0 or int(connections) < min_connection:
                min_connection = int(connections)
                min_connection_port = int(port)
    return min_connection_port

def get_messages():
    global s
    global port
    while True:
        data = s.recv(1024)

        if not data:
            print("Disconnected from server. Reconnecting.")
            s.close()
            r.hset("ports", port, int(r.hget("ports", port)) - 1)
            s = socket.socket()
            port = find_port()
            try:
                s.connect(('127.0.0.1', port))
                print("Connected to PORT ", port)
            except OSError:    
                print("COuldn't connect. You'll be disconnected.")
                break
            s.send(f"{name} has joined the chat".encode())
            print("You've joined the chat.")
            continue
        
        print({data.decode()})

thread1 = threading.Thread(target=get_messages, args=(), daemon= True)
thread1.start()

while True:
    try:
        s.send(input(f"{name} >>> ").encode())
    except OSError:
        print("Try to type once more.")