import socket
import threading
import os
import sys
import time

s = socket.socket()

port = sys.argv[1]

s.connect(('127.0.0.1', int(port)))

name = input("What is your name? ")
s.send(f"{name} has joined the chat".encode())

def get_messages():
    global s
    while True:
        data = s.recv(1024)

        if not data:
            print("Disconnected from server. Reconnecting.")
            s.close()
            s = socket.socket()
            ## TODO: look port table on redis to determine a port, remove hard coded 8080
            s.connect(('127.0.0.1', 8080))
            s.send(f"{name} has joined the chat".encode())
            continue
        
        print({data.decode()})

thread1 = threading.Thread(target=get_messages, args=(), daemon= True)
thread1.start()

while True:
    try:
        s.send(input(f"{name} >>> ").encode())
    except OSError:
        time.sleep(1)
        try:
            s.send(input(f"{name} >>> ").encode())
        except OSError:
            print("Still reconnecting...")