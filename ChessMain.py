import ChessEngine
import pygame as p
import math
import random
import Connect
import time
from _thread import *


height = 512
width = 512
dim = 8
SQ_SIZE = height // dim
MAXFPS = 30
IMAGES = {}
# create waiting for player screen


def loadIMAGES():
    global yc
    yc = n.id
    pieces = ["wp", "wR", "wN", "wB", "wQ",
              "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    if yc == "w":
        for piece in pieces:
            IMAGES[piece] = p.transform.scale(p.image.load(
                "images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    else:
        for piece in pieces:
            IMAGES[piece] = p.transform.scale(p.image.load(
                "images2/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def con():
    global n
    n = Connect.Network()
    main()


def main():
    p.init()
    screen = p.display.set_mode((width, height))
    clock = p.time.Clock()
    screen.fill(p.Color("White"))

    gs = ChessEngine.GameState()
    if n.id != "w":
        gs.whiteToMove = not gs.whiteToMove
    validMoves = gs.getValidMoves()
    animate = True
    loadIMAGES()
    running = True
    created = False

    sqSelected = ()
    playerClicks = []

    start_new_thread(findMove, (gs,))
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN and gs.whiteToMove and n.isReady == True:
                location = p.mouse.get_pos()
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if sqSelected == (row, col):
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)

                if len(playerClicks) == 2:
                    move = ChessEngine.Move(
                        playerClicks[0], playerClicks[1], gs.board)
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            gs.makeMove(validMoves[i])
                            n.send(validMoves[i])
                            n.moveMade = True
                            sqSelected = ()
                            playerClicks = []
                    if not n.moveMade:
                        playerClicks = [sqSelected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_l:
                    gs.undoMove()
                    sqSelected = ()
                    playerClicks = []
                    n.moveMade = True
                    animate = False
        drawGameState(screen, gs, validMoves, sqSelected)
        clock.tick(MAXFPS)
        p.display.flip()
        if n.moveMade == True:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            n.moveMade = False
            animate = True

        # fix for when board is flipped
        if gs.checkMate:
            print("Black wins by checkmate") if gs.whiteToMove else print(
                "White wins by checkmate")
            running = False

        if gs.stalemate:
            print("Draw by stalemate")
            running = False


def madeMove():
    n.moveMade = True


def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(150)
            s.fill(p.Color(117, 199, 233))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(
                        s, (SQ_SIZE * move.endCol, SQ_SIZE * move.endRow))


def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)
    if n.isReady == False:
        show = "Waiting for Player"
        font = p.font.SysFont("comicsans", 80)
        txt = font.render(show, 1, (255, 0, 0))
        screen.blit(
            txt, (round(height/2 - txt.get_width()/2), round(height / 2.25)))


def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color(75, 115, 153)]
    if n.id == "b":
        colors = [p.Color(75, 115, 153), p.Color("white")]
    for r in range(dim):
        for c in range(dim):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(
                c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for r in range(dim):
        for c in range(dim):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(
                    c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def animateMove(move, screen, board, clock):
    global colors
    coords = []
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 8
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = ((move.startRow + dR*frame/frameCount,
                 move.startCol + dC*frame/frameCount))
        drawBoard(screen)
        drawPieces(screen, board)
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(round(move.endCol*SQ_SIZE),
                           round(move.endRow*SQ_SIZE), SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        screen.blit(IMAGES[move.pieceMoved], p.Rect(
            round(c*SQ_SIZE), round(r*SQ_SIZE), SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(110)


def findMove(gs):
    n.send_Ready()
    while True:
        if not gs.whiteToMove and n.online:
            data = n.reciveMoves()
            if data:
                data.startRow = 7 - data.startRow
                data.endRow = 7 - data.endRow
                piece = data.pieceMoved
                newPiece = "b" + str(piece[1])
                data.pieceMoved = newPiece
                print("Recieved move:", data)
                gs.makeMove(data)
                madeMove()


if __name__ == "__main__":
    con()
