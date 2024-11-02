# ChessMain.py
import pygame as pg
import pygame.time
import ChessEngine
from network import ChessClient
import json
import threading
from queue import Queue
import os

pg.init()
screen_info = pg.display.Info()
screen_width, screen_height = screen_info.current_w, screen_info.current_h
board_size = int(min(screen_width, screen_height) * 0.91)
width = height = board_size
dimension = 8
sq_size = board_size // dimension
max_fps = 15
images = {}
screen = pg.display.set_mode((board_size, board_size))

# Global game state variables
player_color = None
is_my_turn = False
game_started = False
move_queue = Queue()

def handle_connection_status(connected):
    if connected:
        print("✓ Connected to server successfully!")
    else:
        print("✗ Disconnected from server")

def loadImages():
    base_dir = os.path.join(os.path.dirname(__file__), "Images_SVG")
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        images[piece] = pg.transform.scale(
            pg.image.load(os.path.join(base_dir, piece + ".svg")),
            (int(sq_size * 2.5), int(sq_size * 2.5))
        )

def handle_network_message(message):
    global player_color, is_my_turn, game_started
    
    try:
        if message["type"] == "game_found":
            player_color = message["color"]
            game_started = True
            is_my_turn = (player_color == "white")
            print(f"Game started! You are playing as {player_color}")
            
        elif message["type"] == "move":
            move_queue.put(message["move"])
            
        elif message["type"] == "game_over":
            print(f"Game Over: {message['result']}")
            
    except Exception as e:
        print(f"Error handling network message: {e}")

def main():
    global is_my_turn, game_started
    
    # Initialize network connection
    network = ChessClient()
    network.set_connection_callback(handle_connection_status)
    
    if not network.connect():
        print("Failed to connect to server")
        return
    
    network.set_game_callback(handle_network_message)
    
    # Find a game
    print("Looking for a game...")
    network.find_game()
    
    screen = pg.display.set_mode((width, height), pg.RESIZABLE)
    clock = pg.time.Clock()
    screen.fill(pg.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []
    
    # Game status text
    font = pg.font.Font(None, 36)
    
    while running:
        # Process any received moves from the network
        while not move_queue.empty():
            move_notation = move_queue.get()
            try:
                start_sq = (int(move_notation[1]), int(move_notation[0]))
                end_sq = (int(move_notation[3]), int(move_notation[2]))
                move = ChessEngine.Move(start_sq, end_sq, gs.board)
                gs.makeMove(move)
                moveMade = True
                is_my_turn = True
            except Exception as e:
                print(f"Error processing received move: {e}")
        
        for e in pg.event.get():
            if e.type == pg.QUIT:
                network.disconnect()
                running = False
                
            elif e.type == pg.MOUSEBUTTONDOWN and game_started and is_my_turn:
                location = pg.mouse.get_pos()
                col = location[0] // sq_size
                row = location[1] // sq_size
                
                if sqSelected == (row, col):
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)
                    
                if len(playerClicks) == 2:
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            gs.makeMove(validMoves[i])
                            moveMade = True
                            is_my_turn = False
                            
                            try:
                                move_notation = str(move.getChessNotation())
                                network.send_move(move_notation)
                            except Exception as e:
                                print(f"Error sending move: {e}")
                                
                            sqSelected = ()
                            playerClicks = []
                            
                    if not moveMade:
                        playerClicks = [sqSelected]
                        
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_z:
                    pass  # Ignore undo in multiplayer
                    
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
            
        drawGameState(screen, gs)
        
        # Draw game status
        status_text = ""
        if not game_started:
            status_text = "Waiting for opponent..."
        elif is_my_turn:
            status_text = "Your turn"
        else:
            status_text = "Opponent's turn"
            
        status_surface = font.render(status_text, True, pg.Color("black"))
        screen.blit(status_surface, (10, 10))
        
        # Draw player color when game has started
        if game_started:
            color_text = f"Playing as: {player_color}"
            color_surface = font.render(color_text, True, pg.Color("black"))
            screen.blit(color_surface, (10, 50))
        
        clock.tick(max_fps)
        pg.display.flip()

def drawGameState(screen, gs):
    drawBoard(screen)
    drawPieces(screen, gs.board)

def drawBoard(screen):
    colors = [pg.Color("white"), pg.Color("purple")]
    for r in range(dimension):
        for c in range(dimension):
            color = colors[((r + c) % 2)]
            pg.draw.rect(screen, color, pg.Rect(c * sq_size, r * sq_size, sq_size, sq_size))

def drawPieces(screen, board):
    for r in range(dimension):
        for c in range(dimension):
            piece = board[r][c]
            if piece != "--":
                screen.blit(images[piece], pg.Rect(c * sq_size, r * sq_size, sq_size, sq_size))

if __name__ == "__main__":
    main()
