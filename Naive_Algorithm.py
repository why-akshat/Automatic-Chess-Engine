class GameState:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunction = {
            'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
            'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves
        }
        self.whiteToMove = True
        self.moveLogs = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.pins = []
        self.checks = []
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()     # Coordinates for the square where enpassant capture is possible
        self.currentCastleRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastleRight.wks, self.currentCastleRight.bks,
                                             self.currentCastleRight.wqs, self.currentCastleRight.bqs)]
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLogs.append(move)
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        # Pawn Promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
        # Enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"

        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.endRow + move.startRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()

        # Castle Moves
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:    # King side castle
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]   # moves the rook into its new square
                self.board[move.endRow][move.endCol+1] = '--'   # erase the rook
            else:   # Queen side castle
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]   # moves the rook into its new square
                self.board[move.endRow][move.endCol21] = '--'   # erase the rook


        # Update castling rights - whenever it is a rook or a king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastleRight.wks, self.currentCastleRight.bks,
                                                 self.currentCastleRight.wqs, self.currentCastleRight.bqs))


    def undoMove(self):
        if len(self.moveLogs) != 0:
            move = self.moveLogs.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            # Undo enpassant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            # Undo a 2 square pawn advance
            if move.pieceMoved[1] == 'P' and abs(move.endRow - move.startRow) == 2:
                self.enpassantPossible = ()

            # undo castling rights
            self.castleRightsLog.pop()  # get rid of new castle rights from the move we are undoing
            self.currentCastleRight = self.castleRightsLog[-1]  # set current castle rights to last one in list

            # undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:    # King side
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else:   # Queen side
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = '--'

    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.currentCastleRight.wks = False
            self.currentCastleRight.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastleRight.bks = False
            self.currentCastleRight.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:  # Left Rook
                    self.currentCastleRight.wqs = False
                elif move.startCol == 7:  # Right Rook
                    self.currentCastleRight.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:  # Left Rook
                    self.currentCastleRight.bqs = False
                elif move.startCol == 7:  # Right Rook
                    self.currentCastleRight.bks = False

    '''
    Naive Algorithm for calculating valid moves
    '''
    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastlingRights = CastleRights(self.currentCastleRight.wks, self.currentCastleRight.bks,
                                          self.currentCastleRight.wqs, self.currentCastleRight.bqs)  # Copy the current castling rights
        moves = self.getAllPossibleMoves()  # First generating all possible moves
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])   # Trying to make that valid move
            self.whiteToMove = not self.whiteToMove   # Validating if that move checks our king or not
            if self.inCheck():
                moves.remove(moves[i])   # Remove that move if in check
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        if len(moves) == 0:  # Either checkmate or stalemate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastleRight = tempCastlingRights
        return moves


    def inCheck(self):   # Is King in check
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove  # switch to opponents turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # switch back turn
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:  # Square is under attack
                return True
        return False

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[0])):
                color = self.board[r][c][0]
                if (color == 'w' and self.whiteToMove) or (color == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunction[piece](r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):  # add all possible pawn moves
        if self.whiteToMove:  # White turn to move
            if self.board[r-1][c] == "--":  # Move 1 square
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--":  # Move 2 square
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c-1 >= 0:  # Capture left piece diagonally
                if self.board[r-1][c-1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c-1), self.board))
                elif (r-1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, True))

            if c+1 <= 7:   # Capture right piece diagonally
                if self.board[r-1][c+1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r-1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, True))

        else:  # Black pawn to move
            if self.board[r+1][c] == "--":  # Move 1 square
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":  # Move 2 square
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c-1 >= 0:  # Capture left piece diagonally
                if self.board[r+1][c-1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c-1), self.board))
                elif (r+1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, True))
            if c+1 <= 7:   # Capture right piece diagonally
                if self.board[r+1][c+1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r+1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, True))

    def getRookMoves(self, r, c, moves):  # add all possible rook moves
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # Possible directions for rook
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # Capture enemy piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))


    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break


    def getQueenMoves(self, r, c, moves):
       self.getRookMoves(r, c, moves)
       self.getBishopMoves(r, c, moves)


    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:    # not ally piece (empty or enemy piece)
                    moves.append(Move((r, c), (endRow, endCol), self.board))



    '''
    Generate all the castle moves for the king at (r, c) and add them to the list of moves
    '''

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c, ):
            return  # Can't castle while in check
        if (self.whiteToMove and self.currentCastleRight.wks) or (not self.whiteToMove and self.currentCastleRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastleRight.wqs) or (not self.whiteToMove and self.currentCastleRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove = True))
    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():

    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}

    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]


        # Pawn Promotion
        self.isPawnPromotion = False
        if (self.pieceMoved == "wP" and self.endRow == 0) or (self.pieceMoved == "bP" and self.endRow == 7):
            self.isPawnPromotion = True

        # Enpassant Move
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wP" if self.pieceMoved == "bP" else "bP"

        # Castle Move
        self.isCastleMove = isCastleMove
        self.moveID = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol


    def __eq__(self, other):
        if(isinstance(other,Move)):
            return self.moveID == other.moveID
        return False
    def getChessNotation(self):
        return self.getRankFiles(self.startRow, self.startCol) + self.getRankFiles(self.endRow, self.endCol)

    def getRankFiles(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]


    '''
    Advanced Algorithm to get valid moves
    '''

    # def getValidMoves(self):
    #     moves = []
    #     self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
    #     if self.whiteToMove:
    #         kingRow, kingCol = self.whiteKingLocation
    #     else:
    #         kingRow, kingCol = self.blackKingLocation
    #     if self.inCheck:
    #         if len(self.checks) == 1:  # only 1 check, block the check or move the king
    #             moves = self.getAllPossibleMoves()
    #             # to block a check you must move a piece into one of the squares between the enemy piece and the king
    #             check = self.checks[0]  # check information
    #             checkRow, checkCol = check[:2]
    #             pieceChecking = self.board[checkRow][checkCol]  # enemy piece causing the check
    #             validSquares = []  # squares that pieces can move to
    #             # if knight, must capture knight or move king, other pieces can be blocked
    #             if pieceChecking[1] == 'N':
    #                 validSquares = [(checkRow, checkCol)]
    #             else:
    #                 for i in range(1, 8):
    #                     validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
    #                     validSquares.append(validSquare)
    #                     if validSquare == (checkRow, checkCol):  # once you get to piece and checks
    #                         break
    #             # get rid of any moves that don't block check or move king
    #             for i in range(len(moves) - 1, -1, -1):
    #                 if moves[i].pieceMoved[1] != 'K':  # move doesn't move king, so it must block or capture
    #                     if not (moves[i].endRow, moves[i].endCol) in validSquares:  # move doesn't block check or capture piece
    #                         moves.remove(moves[i])
    #         else:  # double check, king has to move
    #             self.getKingMoves(kingRow, kingCol, moves)
    #     else:  # not in check so all moves are fine
    #         moves = self.getAllPossibleMoves()
    #
    #     return moves
    #
    # def getAllPossibleMoves(self):
    #     moves = []
    #     for r in range(len(self.board)):
    #         for c in range(len(self.board[r])):
    #             color = self.board[r][c][0]
    #             if (color == 'w' and self.whiteToMove) or (color == 'b' and not self.whiteToMove):
    #                 piece = self.board[r][c][1]
    #                 self.moveFunction[piece](r, c, moves)
    #     return moves
    #
    # def getPawnMoves(self, r, c, moves):
    #     piecePinned = False
    #     pinDirection = ()
    #     for i in range(len(self.pins) - 1, -1, -1):
    #         if self.pins[i][0] == r and self.pins[i][1] == c:
    #             piecePinned = True
    #             pinDirection = (self.pins[i][2], self.pins[i][3])
    #             self.pins.remove(self.pins[i])
    #             break
    #     if self.whiteToMove:  # white pawn moves
    #         if self.board[r - 1][c] == "--":  # 1 square move
    #             if not piecePinned or pinDirection == (-1, 0):
    #                 moves.append(Move((r, c), (r - 1, c), self.board))
    #                 if r == 6 and self.board[r - 2][c] == "--":
    #                     moves.append(Move((r, c), (r - 2, c), self.board))
    #         if c - 1 >= 0:  # capture to the left
    #             if self.board[r - 1][c - 1][0] == 'b':
    #                 if not piecePinned or pinDirection == (-1, -1):
    #                     moves.append(Move((r, c), (r - 1, c - 1), self.board))
    #         if c + 1 <= 7:  # capture to the right
    #             if self.board[r - 1][c + 1][0] == 'b':
    #                 if not piecePinned or pinDirection == (-1, 1):
    #                     moves.append(Move((r, c), (r - 1, c + 1), self.board))
    #     else:  # black pawn moves
    #         if self.board[r + 1][c] == "--":
    #             if not piecePinned or pinDirection == (1, 0):
    #                 moves.append(Move((r, c), (r + 1, c), self.board))
    #                 if r == 1 and self.board[r + 2][c] == "--":
    #                     moves.append(Move((r, c), (r + 2, c), self.board))
    #         if c - 1 >= 0:
    #             if self.board[r + 1][c - 1][0] == 'w':
    #                 if not piecePinned or pinDirection == (1, -1):
    #                     moves.append(Move((r, c), (r + 1, c - 1), self.board))
    #         if c + 1 <= 7:
    #             if self.board[r + 1][c + 1][0] == 'w':
    #                 if not piecePinned or pinDirection == (1, 1):
    #                     moves.append(Move((r, c), (r + 1, c + 1), self.board))
    #
    # def getRookMoves(self, r, c, moves):
    #     piecePinned = False
    #     pinDirection = ()
    #     for i in range(len(self.pins) - 1, -1, -1):
    #         if self.pins[i][0] == r and self.pins[i][1] == c:
    #             piecePinned = True
    #             pinDirection = (self.pins[i][2], self.pins[i][3])
    #             if self.board[r][c][1] != 'Q':
    #                 self.pins.remove(self.pins[i])
    #             break
    #     directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
    #     enemyColor = "b" if self.whiteToMove else "w"
    #     for d in directions:
    #         for i in range(1, 8):
    #             endRow = r + d[0] * i
    #             endCol = c + d[1] * i
    #             if 0 <= endRow < 8 and 0 <= endCol < 8:
    #                 if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
    #                     endPiece = self.board[endRow][endCol]
    #                     if endPiece == "--":
    #                         moves.append(Move((r, c), (endRow, endCol), self.board))
    #                     elif endPiece[0] == enemyColor:
    #                         moves.append(Move((r, c), (endRow, endCol), self.board))
    #                         break
    #                     else:
    #                         break
    #             else:
    #                 break
    #
    # def getKnightMoves(self, r, c, moves):
    #     piecePinned = False
    #     for i in range(len(self.pins) - 1, -1, -1):
    #         if self.pins[i][0] == r and self.pins[i][1] == c:
    #             piecePinned = True
    #             self.pins.remove(self.pins[i])
    #             break
    #     knightMoves = ((-2, -1), (-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1))
    #     allyColor = "w" if self.whiteToMove else "b"
    #     for m in knightMoves:
    #         endRow = r + m[0]
    #         endCol = c + m[1]
    #         if 0 <= endRow < 8 and 0 <= endCol < 8:
    #             endPiece = self.board[endRow][endCol]
    #             if endPiece[0] != allyColor:
    #                 if not piecePinned:
    #                     moves.append(Move((r, c), (endRow, endCol), self.board))
    #
    # def getBishopMoves(self, r, c, moves):
    #     piecePinned = False
    #     pinDirection = ()
    #     for i in range(len(self.pins) - 1, -1, -1):
    #         if self.pins[i][0] == r and self.pins[i][1] == c:
    #             piecePinned = True
    #             pinDirection = (self.pins[i][2], self.pins[i][3])
    #             self.pins.remove(self.pins[i])
    #             break
    #     directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
    #     enemyColor = "b" if self.whiteToMove else "w"
    #     for d in directions:
    #         for i in range(1, 8):
    #             endRow = r + d[0] * i
    #             endCol = c + d[1] * i
    #             if 0 <= endRow < 8 and 0 <= endCol < 8:
    #                 if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
    #                     endPiece = self.board[endRow][endCol]
    #                     if endPiece == "--":
    #                         moves.append(Move((r, c), (endRow, endCol), self.board))
    #                     elif endPiece[0] == enemyColor:
    #                         moves.append(Move((r, c), (endRow, endCol), self.board))
    #                         break
    #                     else:
    #                         break
    #             else:
    #                 break
    #
    # def getQueenMoves(self, r, c, moves):
    #     self.getRookMoves(r, c, moves)
    #     self.getBishopMoves(r, c, moves)
    #
    # def getKingMoves(self, r, c, moves):
    #     kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
    #     allyColor = "w" if self.whiteToMove else "b"
    #     for i in range(8):
    #         endRow = r + kingMoves[i][0]
    #         endCol = c + kingMoves[i][1]
    #         if 0 <= endRow < 8 and 0 <= endCol < 8:
    #             endPiece = self.board[endRow][endCol]
    #             if endPiece[0] != allyColor:
    #                 # place king on end square and check for checks
    #                 if self.whiteToMove:
    #                     self.whiteKingLocation = (endRow, endCol)
    #                 else:
    #                     self.blackKingLocation = (endRow, endCol)
    #                 inCheck, pins, checks = self.checkForPinsAndChecks()
    #                 if not inCheck:
    #                     moves.append(Move((r, c), (endRow, endCol), self.board))
    #                 if self.whiteToMove:
    #                     self.whiteKingLocation = (r, c)
    #                 else:
    #                     self.blackKingLocation = (r, c)
    #
    # def checkForPinsAndChecks(self):
    #     pins = []
    #     checks = []
    #     inCheck = False
    #     if self.whiteToMove:
    #         enemyColor = "b"
    #         allyColor = "w"
    #         startRow = self.whiteKingLocation[0]
    #         startCol = self.whiteKingLocation[1]
    #     else:
    #         enemyColor = "w"
    #         allyColor = "b"
    #         startRow = self.blackKingLocation[0]
    #         startCol = self.blackKingLocation[1]
    #     directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
    #     for j in range(len(directions)):
    #         d = directions[j]
    #         possiblePin = ()
    #         for i in range(1, 8):
    #             endRow = startRow + d[0] * i
    #             endCol = startCol + d[1] * i
    #             if 0 <= endRow < 8 and 0 <= endCol < 8:
    #                 endPiece = self.board[endRow][endCol]
    #                 if endPiece[0] == allyColor and endPiece[1] != 'K':
    #                     if possiblePin == ():
    #                         possiblePin = (endRow, endCol, d[0], d[1])
    #                     else:
    #                         break
    #                 elif endPiece[0] == enemyColor:
    #                     type = endPiece[1]
    #                     if (0 <= j <= 3 and type == 'R') or \
    #                             (4 <= j <= 7 and type == 'B') or \
    #                             (i == 1 and type == 'P' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
    #                             (type == 'Q') or (i == 1 and type == 'K'):
    #                         if possiblePin == ():
    #                             inCheck = True
    #                             checks.append((endRow, endCol, d[0], d[1]))
    #                             break
    #                         else:
    #                             pins.append(possiblePin)
    #                             break
    #                     else:
    #                         break
    #             else:
    #                 break
    #     knightMoves = ((-2, -1), (-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1))
    #     for m in knightMoves:
    #         endRow = startRow + m[0]
    #         endCol = startCol + m[1]
    #         if 0 <= endRow < 8 and 0 <= endCol < 8:
    #             endPiece = self.board[endRow][endCol]
    #             if endPiece[0] == enemyColor and endPiece[1] == 'N':
    #                 inCheck = True
    #                 checks.append((endRow, endCol, m[0], m[1]))
    #     return inCheck, pins, checks

