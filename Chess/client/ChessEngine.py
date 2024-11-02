class GameState():
    def __init__(self):
        # board is 2D with 8*8
        # b for black w for white
        # "--" is for empty space
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunctions = {}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation=(7,4)
        self.blackKingLocation=(0,4)
        self.checkMate=False
        self.staleMate=False
        self.enpassantPossible=() #coordinate where it is possible

    def makeMove(self, move):
        if self.isValidMove(move):
            self.board[move.startRow][move.startCol] = "--"
            self.board[move.endRow][move.endCol] = move.pieceMoved
            self.moveLog.append(move)  # move is stored so that undo is possible
            self.whiteToMove = not self.whiteToMove  # switch turns
            #updating kings loc
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.endRow,move.endCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.endRow,move.endCol)

            if move.isPawnPromotion:
                self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

    def undoMove(self):
        if len(self.moveLog) != 0:  # make sure move is done
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # switch turns
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow,move.startCol)
            elif move.pieceMoved == 'bK':
                self.whiteKingLocation = (move.startRow,move.startCol)

    def isValidMove(self, move):
        # Check if the move is valid based on whose turn it is
        piece = move.pieceMoved
        if (self.whiteToMove and piece[0] == 'w') or (not self.whiteToMove and piece[0] == 'b'):
            return True
        return False

    # moves when under check
    def getValidMoves(self):
        moves=self.getAllPossibleMoves() #generate all possible moves
        for i in range(len(moves)-1,-1,-1):#move is made for each case
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i]) # if king is attacked not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0: #either checkmate or stalemate
            if self.inCheck():
                self.checkMate=True
            else:
                self.staleMate=True
        else:
            self.checkMate=False
            self.staleMate=False
        return moves



    def inCheck(self):#determines if in check
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0],self.blackKingLocation[1])

    def squareUnderAttack(self,r,c):#if enemy can attack square r,c
        self.whiteToMove=not self.whiteToMove #switch to opponents turn
        oppMoves=self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c: # square under attack
                return True
        return False
    # moves when not under check
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):  # no of rows
            for c in range(len(self.board[r])):  # no of cols in given row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    if piece == 'p':
                        self.getPawnMoves(r, c, moves)
                    elif piece == 'R':
                        self.getRookMoves(r, c, moves)
                    elif piece == 'N':
                        self.getKnightMoves(r, c, moves)
                    elif piece == 'B':
                        self.getBishopMoves(r, c, moves)
                    elif piece == 'Q':
                        self.getQueenMoves(r, c, moves)
                    elif piece == 'K':
                        self.getKingMoves(r, c, moves)
        return moves
    # collects all moves of pawns
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove: #white pawn moves
            if self.board[r-1][c] == "--": #one square move
                moves.append(Move((r,c),(r-1,c),self.board))
                if r == 6 and self.board[r-2][c] == "--": #2 sq move
                    moves .append(Move((r,c),(r-2,c),self.board))
            if c - 1 >= 0: #captures to left
                if self.board[r-1][c-1][0]=='b': #black to capture
                    moves.append(Move((r, c), (r - 1, c-1), self.board))
            if c + 1 <= 7: #captures to right
                if self.board[r-1][c+1][0]=='b':
                    moves.append(Move((r, c), (r - 1, c+1), self.board))
        else: #black pawn moves
            if self.board[r+1][c] == "--":
                moves.append(Move((r,c),(r+1,c),self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c - 1 >= 0:
                if self.board[r+1][c-1][0] == "w":
                        moves.append(Move((r, c), (r+1, c-1), self.board))
            if c + 1 <= 7:
                if self.board[r+1][c+1][0] == "w":
                        moves.append(Move((r,c),(r+1,c+1),self.board))


    def getRookMoves(self, r, c, moves):
        direction=((-1,0),(0,-1),(1,0),(0,1))#up,left,down,right resp
        if self.whiteToMove:
            enemy="b"
        else:
            enemy="w"
        for d in direction:
            for i in range(1,8):
                endRow=r+d[0]*i
                endCol=c+d[1]*i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece=self.board[endRow][endCol]
                    if endPiece == "--": #if empty space
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0]==enemy: #if enemy piece(valid)
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else: #friendly piece invalid
                        break
                else: #offboard
                    break

    def getKnightMoves(self, r, c, moves):
        direction=((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        if self.whiteToMove:
            enemy="b"
        else:
            enemy="w"
        for d in direction:
            endRow=r+d[0]
            endCol=c+d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece=self.board[endRow][endCol]
                if endPiece[0] == enemy or endPiece == "--":
                    moves.append(Move((r,c),(endRow,endCol),self.board))

    def getBishopMoves(self, r, c, moves):
        direction=((-1,-1),(-1,1),(1,-1),(1,1))
        if self.whiteToMove:
            enemy="b"
        else:
            enemy="w"
        for d in direction:
            for i in range(1,8):
                endRow=r+d[0]*i
                endCol=c+d[1]*i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece=self.board[endRow][endCol]
                    if endPiece=="--":
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0]==enemy:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else:
                        break
                else:
                    break

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)

    def getKingMoves(self, r, c, moves):
        kingMoves=((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
        if self.whiteToMove:
            enemy="b"
        else:
            enemy="w"
        for i in range(8):
            endRow=r+kingMoves[i][0]
            endCol=c+kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece=self.board[endRow][endCol]
                if endPiece[0] == enemy or endPiece == "--":
                    moves.append(Move((r,c),(endRow,endCol),self.board))


class Move():
    # maps keys to values using dictionary
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, enpassantPossible = ()):  # to validate the move
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        # Store the info of move
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = False
        if (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7):
            self.isPawnPromotion = True

        self.isEnpassantMove = False
        if self.pieceMoved[1] == 'p' and (self.endRow,self.endCol) == enpassantPossible:
            self.isEnpassantMove = True
        self.moveID=self.startRow*1000+self.startCol*100+self.endRow*10+self.endCol

    #overriding equals method
    def __eq__(self,other):
        if isinstance(other,Move):
            return self.moveID==other.moveID
        return False

    def getChessNotation(self):  # official chess notations
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
