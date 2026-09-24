import socket
import threading
import os
import sys
import redis
from dotenv import load_dotenv

class ChatClient:
    def __init__(self, initial_port):
        load_dotenv()

        self.redis_url = os.getenv("REDIS_URL")
        self.r = redis.Redis.from_url(self.redis_url, decode_responses=True)

        self.port = int(initial_port)
        self.s = socket.socket()
        self.name = ""
        self.running = True


    def start(self):
        self.name = input("What is your name? ").strip()
        if len(self.name) == 0:
            print("Name can't be empty.")
            return
        
        self.connect_to_server()

        thread1 = threading.Thread(target=self.get_message, args=(), daemon= True)
        thread1.start()

        while self.running:
            try:
                user_input = input(f"{self.name} >>> ").strip()
                if not self.running: 
                    break
                if user_input:
                    self.s.sendall(user_input.encode())
            except OSError:
                if self.running:
                    continue
                else:
                    break

        self.s.close()

    def connect_to_server(self):
        try:
            self.s.connect(('127.0.0.1', self.port))
            print(f"Connected to server on PORT {self.port}!")
            self.s.sendall(f"{self.name} has joined the chat".encode())

        except OSError:
            print(f"Couldn't connect to PORT {self.port}. Trying another port.")
            self.handle_reconnection()
    
    def handle_reconnection(self):
        self.s.close()

        current_port_count = self.r.hget("ports", str(self.port))

        if current_port_count and int(current_port_count) > 0:
            self.r.hset("ports", str(self.port), int(current_port_count) - 1)

        another_port = self.find_port()

        if another_port is None:
            print("No other ports found. Disconnecting.")
            self.running = False
            sys.exit(1)

        self.port = another_port
        self.s = socket.socket()
        self.connect_to_server()

    def find_port(self):
        every_port = self.r.hgetall("ports")
        min_connection = 0
        min_connection_port = 0

        for port, connections in every_port.items():
            if int(connections) > 0:
                
                if min_connection == 0 or int(connections) < min_connection:
                    min_connection = int(connections)
                    min_connection_port = int(port)

        return min_connection_port

    def get_message(self):
        while self.running:
            try:
                data = self.s.recv(1024)

                if not data:
                    if self.running:
                        self.handle_reconnection()
                    break
                
                print(f"\n{data.decode()}")
                print(f"{self.name} >>> ", end="", flush=True)
            except OSError:
                if self.running:
                    self.handle_reconnection()
                break

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("python3 client.py <PORT>")
        sys.exit(1)
        
    client = ChatClient(initial_port=sys.argv[1])
    client.start()