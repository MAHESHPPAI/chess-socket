# network.py
import socket
import json
import threading

class ChessClient:
    def __init__(self, host='localhost', port=5555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = (host, port)
        self.game_callback = None
        self.connected = False
        self.connection_callback = None

    def connect(self):
        try:
            print(f"Attempting to connect to {self.addr[0]}:{self.addr[1]}...")
            self.client.connect(self.addr)
            self.connected = True
            print("Successfully connected to server!")
            
            # Send initial connection message
            message = {
                "type": "connect",
                "message": "New client connected"
            }
            self.client.send(json.dumps(message).encode())
            
            # Start receiving messages in a separate thread
            thread = threading.Thread(target=self.receive_messages)
            thread.daemon = True
            thread.start()
            
            if self.connection_callback:
                self.connection_callback(True)
            return True
            
        except Exception as e:
            print(f"Connection error: {e}")
            if self.connection_callback:
                self.connection_callback(False)
            return False

    def disconnect(self):
        if self.connected:
            try:
                self.client.close()
                self.connected = False
                print("Disconnected from server")
                if self.connection_callback:
                    self.connection_callback(False)
            except Exception as e:
                print(f"Error disconnecting: {e}")

    def is_connected(self):
        return self.connected

    def send_move(self, move):
        if not self.connected:
            print("Not connected to server!")
            return
        try:
            message = {
                "type": "move",
                "move": move
            }
            self.client.send(json.dumps(message).encode())
        except Exception as e:
            print(f"Error sending move: {e}")
            self.handle_connection_loss()

    def find_game(self):
        if not self.connected:
            print("Not connected to server!")
            return
        try:
            message = {
                "type": "find_game"
            }
            self.client.send(json.dumps(message).encode())
        except Exception as e:
            print(f"Error finding game: {e}")
            self.handle_connection_loss()

    def receive_messages(self):
        while self.connected:
            try:
                data = self.client.recv(2048).decode()
                if not data:
                    self.handle_connection_loss()
                    break
                
                message = json.loads(data)
                print(f"Received message: {message}")
                
                if self.game_callback:
                    self.game_callback(message)
                    
            except json.JSONDecodeError as e:
                print(f"Error decoding message: {e}")
            except Exception as e:
                print(f"Error receiving message: {e}")
                self.handle_connection_loss()
                break

    def handle_connection_loss(self):
        self.connected = False
        print("Lost connection to server!")
        if self.connection_callback:
            self.connection_callback(False)

    def set_game_callback(self, callback):
        self.game_callback = callback
        
    def set_connection_callback(self, callback):
        self.connection_callback = callback