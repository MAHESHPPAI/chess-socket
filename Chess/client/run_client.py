# client/run_client.py
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.ChessMain import main

if __name__ == "__main__":
    main()