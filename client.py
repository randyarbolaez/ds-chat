import socket
import threading

s = socket.socket()

port = 8080

s.connect(('127.0.0.1', port))

name = input("What is your name? ")
s.send(f"{name} has joined the chat".encode())

def get_messages(s):
    while True:
        data = s.recv(1024)

        if not data:
            break
        print({data.decode()})

thread1 = threading.Thread(target=get_messages, args=(s,), daemon= True)
thread1.start()

while True:
    s.send(input(f"{name} >>> ").encode())
    # thread1.join()
