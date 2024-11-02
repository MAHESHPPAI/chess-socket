# server/game_manager.py
import json
from dataclasses import dataclass
from typing import Optional, Dict, List

@dataclass
class Game:
    white_player: int
    black_player: int
    current_turn: str = "white"  # Start with white's turn
    moves: List[str] = None
    
    def __post_init__(self):
        self.moves = []
    
    def make_move(self, move: str, player_id: int) -> bool:
        # Verify it's the player's turn
        if (self.current_turn == "white" and player_id != self.white_player) or \
           (self.current_turn == "black" and player_id != self.black_player):
            return False
        
        # Record the move
        self.moves.append(move)
        
        # Switch turns
        self.current_turn = "black" if self.current_turn == "white" else "white"
        return True
    
    def get_other_player(self, player_id: int) -> Optional[int]:
        """Get the ID of the other player in the game."""
        if player_id == self.white_player:
            return self.black_player
        elif player_id == self.black_player:
            return self.white_player
        return None

class GameManager:
    def __init__(self):
        self.games: List[Game] = []
        self.waiting_players: List[int] = []
        self.player_connections: Dict[int, any] = {}  # Stores socket connections
        
    def add_player_connection(self, player_id: int, connection) -> None:
        """Store the player's connection for future communication."""
        self.player_connections[player_id] = connection
    
    def remove_player(self, player_id: int) -> None:
        """Remove a player from the game system."""
        # Remove from waiting list if present
        if player_id in self.waiting_players:
            self.waiting_players.remove(player_id)
        
        # Remove from connections
        self.player_connections.pop(player_id, None)
        
        # Remove any games with this player
        self.games = [game for game in self.games 
                     if game.white_player != player_id 
                     and game.black_player != player_id]

    def find_or_create_game(self, player_id: int) -> Optional[Game]:
        """Find a game for a player or create a new one if needed."""
        # First check if player is already in a game
        existing_game = self.get_player_game(player_id)
        if existing_game:
            return existing_game
            
        if self.waiting_players:
            other_player = self.waiting_players.pop(0)
            game = Game(white_player=other_player, black_player=player_id)
            self.games.append(game)
            return game
        else:
            self.waiting_players.append(player_id)
            return None

    def get_player_game(self, player_id: int) -> Optional[Game]:
        """Get the game that a player is participating in."""
        for game in self.games:
            if player_id in [game.white_player, game.black_player]:
                return game
        return None

    def broadcast_move(self, player_id: int, move: str) -> bool:
        """Send a move to a specific player."""
        if player_id in self.player_connections:
            try:
                conn = self.player_connections[player_id]
                message = {
                    "type": "move",
                    "move": move
                }
                conn.send(json.dumps(message).encode())
                return True
            except Exception as e:
                print(f"Error broadcasting move: {e}")
                return False
        return False

    def end_game(self, game: Game, reason: str = "Game Over") -> None:
        """End a game and notify both players."""
        if game in self.games:
            message = {
                "type": "game_over",
                "result": reason
            }
            encoded_message = json.dumps(message).encode()
            
            # Notify both players
            for player_id in [game.white_player, game.black_player]:
                if player_id in self.player_connections:
                    try:
                        self.player_connections[player_id].send(encoded_message)
                    except Exception as e:
                        print(f"Error notifying player {player_id} of game end: {e}")
            
            # Remove the game
            self.games.remove(game)