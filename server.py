import socket
import threading

try:
    s = socket.socket()
    print("Socket is successfully created!")
except socket.error as e:
    print("Error creating socket: ", e)

port = 8080
s.bind(('', port))
s.listen(5)

def messages(c,address):
    print(f"Connection from {address}")
    while True:
        data = c.recv(1024)

        if not data:
            break
        print(data.decode())

while True:
    c, address = s.accept()
    thread = threading.Thread(target=messages, args=(c,address), daemon= True)
    thread.start()