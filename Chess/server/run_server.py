# server/run_server.py
import socket
import sys
import os

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))

from server import ChessServer

def main():
    try:
        # You can change these values if needed
        HOST = 'localhost'  # Use '0.0.0.0' to accept connections from any IP
        PORT = 5555

        server = ChessServer(HOST, PORT)
        print(f"Chess server started on {HOST}:{PORT}")
        print("Waiting for players to connect...")
        server.start()
    except Exception as e:
        print(f"Server error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()