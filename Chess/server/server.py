# server/server.py
import socket
import threading
import json
from game_manager import GameManager

class ChessServer:
    def __init__(self, host='localhost', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        self.game_manager = GameManager()
        print(f"Server running on {host}:{port}")

    def handle_client(self, conn, addr):
        player_id = addr[1]  # Using port as player ID for simplicity
        print(f"New connection from {addr}")
        
        try:
            while True:
                data = conn.recv(2048).decode()
                if not data:
                    break
                
                message = json.loads(data)
                if message["type"] == "find_game":
                    game = self.game_manager.find_or_create_game(player_id)
                    response = {
                        "type": "game_found",
                        "color": "white" if game.white_player == player_id else "black"
                    }
                    conn.send(json.dumps(response).encode())
                
                elif message["type"] == "move":
                    game = self.game_manager.get_player_game(player_id)
                    if game:
                        game.make_move(message["move"], player_id)
                        # Broadcast move to other player
                        other_player = game.get_other_player(player_id)
                        self.game_manager.broadcast_move(other_player, message["move"])
        
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
        finally:
            self.game_manager.remove_player(player_id)
            conn.close()

    def start(self):
        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()