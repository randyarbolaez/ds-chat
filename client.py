import socket
import threading
import os

s = socket.socket()

port = 8080

s.connect(('127.0.0.1', port))

name = input("What is your name? ")
s.send(f"{name} has joined the chat".encode())

def get_messages(s):
    while True:
        data = s.recv(1024)

        if not data:
            print("Server disconnected")
            break
        print({data.decode()})
    s.close()
    os._exit(0)

thread1 = threading.Thread(target=get_messages, args=(s,), daemon= True)
thread1.start()

while True:
    s.send(input(f"{name} >>> ").encode())
