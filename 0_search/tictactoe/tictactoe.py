"""
Tic Tac Toe Player
"""

import math
import copy
from random import random, randrange

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    count = 0
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                count += 1
    # if emptys count is even, its X turn
    if count % 2 == 1:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    listactions = []
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                listactions.append((i,j))
    return listactions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i = action[0]
    j = action[1]
    
    # If action is not a valid action for the board, your program should raise an exception.
    if board[i][j] != EMPTY:
        raise Exception("action not valid")

    """
    the original board should be left unmodified: since Minimax will ultimately require considering many 
    different board states during its computation. You'll likely want to make a deep copy of the board 
    first before making any changes.
    """
    result_board = copy.deepcopy(board)
    result_board[i][j] = player(board)

    return result_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # checks horizontally
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != EMPTY:
            return board[i][1]
    # vertically
    for j in range(3):
        if board[0][j] == board[1][j] == board[2][j] != EMPTY:
            return board[1][j]
    # diagonally
    if board[0][0] == board[1][1] == board[2][2] != EMPTY:
        return board[1][1]
    if board[2][0] == board[1][1] == board[0][2] != EMPTY:
        return board[1][1]
    
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board):
        return True
    count = 0
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                count += 1
    # if emptys count is 0, there is no more moves
    if count == 0:
        return True
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    userwinner = winner(board)
    if userwinner == X:
        return 1
    elif userwinner == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    
    if player(board) == X: # MAX
        v = -99
        for action in actions(board):
            val = min_value(result(board, action))
            if val > v:
                options = [action]
                v = val
            elif val == v:
                options.append(action)
           

    elif player(board) == O: # MIN
        v = 99
        for action in actions(board):
            val = max_value(result(board, action))
            if val < v:
                options = [action]
                v = val
            elif val == v:
                options.append(action)
            
    return options[randrange(len(options))]


def max_value(board):
    if terminal(board):
        return utility(board)   
    v = -99
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v


def min_value(board):
    if terminal(board):
        return utility(board)
    v = 99
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v