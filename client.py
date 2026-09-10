import socket
import asyncio

s = socket.socket()

port = 8080

s.connect(('127.0.0.1', port))

name = input("What is your name? ")
s.send(f"{name} has joined the chat".encode())

while True:
    s.send(input(f"{name} >>> ").encode())
