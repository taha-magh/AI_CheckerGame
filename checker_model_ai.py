from config_file import *
from utils import is_in_bound
from move import Move
from piece import Piece
import numpy
import math
import copy
from itertools import product
from checker_model_random import CheckerModelRandom
from checker_model_minmax import CheckerModelMinMax
from checker_model_mtc import CheckerModelMTC

class CheckerModel:
    def __init__(self, checker_grid=None):
        if checker_grid is None:
            self.create_grid()
        else:
            self.checker_grid = checker_grid
        self.turn = 1  # 1 : pour le joueur 1 et -1 pour le joueur 2
        self.dict_of_possible_moves = self.get_possible_moves()
        self.history = []

    def create_grid(self):
        self.checker_grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        for row in range(0, ROWS):
            for col in range(0, COLS):
                if (row + col) % 2 == 0:
                    self.checker_grid[row][col] = math.nan
        for row in range(0, ROWS):
            for col in range(0, COLS):
                if (row + col) % 2 != 0:
                    if row < FILLED_ROWS:  # joueur 2
                        self.checker_grid[row][col] = Piece(row, col, player=-1)
                    elif row > ROWS - FILLED_ROWS - 1:  # joueur 2
                        self.checker_grid[row][col] = Piece(row, col, player=1)

    def move_piece(self, selected_piece_position, move_position):
        self.history.append(copy.deepcopy(self.checker_grid))
        row_selection, col_selection = selected_piece_position
        current_piece = self.checker_grid[row_selection][col_selection]
        current_piece.row, current_piece.col = move_position
        if (self.turn == 1 and current_piece.row == 0) or (self.turn == -1 and current_piece.row == ROWS - 1):
            current_piece.become_king()
        self.checker_grid[row_selection][col_selection] = 0
        self.checker_grid[current_piece.row][current_piece.col] = current_piece
        for possible_move_object in self.dict_of_possible_moves[selected_piece_position]:
            if possible_move_object.get_final_position() == move_position:
                for piece_position_to_attact in possible_move_object.list_attacked_enemy_pieces:
                    row_to_attack, col_to_attack = piece_position_to_attact
                    self.checker_grid[row_to_attack][col_to_attack] = 0
        self.turn = -1 if self.turn == 1 else 1
        self.dict_of_possible_moves = self.get_possible_moves()

    def undo_last_action(self):
        if self.history:
            self.checker_grid = self.history[-1]
            self.history = self.history[:-1]
            self.turn = -1 if self.turn == 1 else 1
            self.dict_of_possible_moves = self.get_possible_moves()

    def get_cell_state(self, row, col):
        if not is_in_bound(row, col):
            return "out_of_bound"
        elif self.checker_grid[row][col] == 0:
            return "accessible"
        elif type(self.checker_grid[row][col]) == Piece:
            piece = self.checker_grid[row][col]
            if piece.player == self.turn:
                return "not_accessible"
            else:
                return "enemy"

    def get_possible_moves(self):
        dict_of_all_moves = dict()
        for row, col in product(range(0, ROWS), range(0, COLS)):
            if type(self.checker_grid[row][col]) == Piece:
                current_piece = self.checker_grid[row][col]
                if current_piece.player == self.turn:
                    depth, all_moves_for_current_piece = self.get_possible_moves_for_current_piece(current_piece, depth=0, all_moves_for_current_piece=[])
                    dict_of_all_moves[(row, col)] = depth, all_moves_for_current_piece
        dict_of_possible_moves = {}
        max_depth = 0
        for piece, (depth, possible_moves_for_current_piece) in dict_of_all_moves.items():
            if depth > max_depth:
                max_depth = depth
                dict_of_possible_moves = {piece: possible_moves_for_current_piece}
            elif depth == max_depth:
                dict_of_possible_moves[piece] = possible_moves_for_current_piece
        return dict_of_possible_moves

    def get_possible_moves_for_current_piece(self, current_piece, depth, all_moves_for_current_piece):
        row, col = current_piece.row, current_piece.col
        cells_to_check = current_piece.get_cells_to_check()
        for row_to_check, col_to_check in cells_to_check:
            stop_verify = False
            for row_to_verify in range(row, row_to_check, 1 if row_to_check > row else -1):
                for col_to_verify in range(col, col_to_check, 1 if col_to_check > col else -1):
                    if type(self.checker_grid[row_to_verify][col_to_verify]) == Piece and row_to_verify != row and col_to_verify != col:
                        stop_verify = True
            if stop_verify:
                pass
            else:
                cell_state = self.get_cell_state(row_to_check, col_to_check)
                if cell_state == "accessible" and depth == 0 and (row_to_check - row != self.turn or current_piece.king):
                    move_object = Move(initial_piece_position=(row, col), list_piece_positions=[(row_to_check, col_to_check)], list_attacked_enemy_pieces=[])
                    all_moves_for_current_piece.append(move_object)
                elif cell_state == "enemy":
                    row_arrival = row_to_check + 1 if row_to_check > row else row_to_check - 1
                    col_arrival = col_to_check + 1 if col_to_check > col else col_to_check - 1
                    if self.get_cell_state(row_arrival, col_arrival) == "accessible":
                        attacked_piece = self.checker_grid[row_to_check][col_to_check]
                        self.checker_grid[row][col] = 0
                        self.checker_grid[row_to_check][col_to_check] = 0
                        self.checker_grid[row_arrival][col_arrival] = current_piece
                        current_piece.row, current_piece.col = row_arrival, col_arrival
                        if depth == 0:
                            move_object = Move(initial_piece_position=(row, col), list_piece_positions=[(row_arrival, col_arrival)], list_attacked_enemy_pieces=[(row_to_check, col_to_check)])
                            all_moves_for_current_piece.append(move_object)
                        else:
                            if depth <= all_moves_for_current_piece[-1].get_depth():
                                current_move_object = all_moves_for_current_piece[-1].extract_common_deplacement(extraction_depth=depth)
                                all_moves_for_current_piece.append(current_move_object)
                            all_moves_for_current_piece[-1].update_move(new_piece_position=(row_arrival, col_arrival), new_attacked_enemy_piece=(row_to_check, col_to_check))
                        self.get_possible_moves_for_current_piece(current_piece, depth + 1, all_moves_for_current_piece)
                        current_piece.row, current_piece.col = row, col
                        self.checker_grid[row][col] = current_piece
                        self.checker_grid[row_to_check][col_to_check] = attacked_piece
                        self.checker_grid[row_arrival][col_arrival] = 0
        max_depth = 0
        possible_moves = []
        for current_move in all_moves_for_current_piece:
            current_move_depth = current_move.get_depth()
            if current_move_depth > max_depth:
                max_depth = current_move_depth
                possible_moves = [current_move]
            elif current_move_depth == max_depth:
                possible_moves.append(current_move)
        return max_depth, possible_moves

    def is_game_over(self):
        # Implement game over logic here
        pass

class CheckerModelAI:
    def __init__(self):
        pass

    def move_piece(self, checker_model, ai="random", **params):
        if params is None:
            params = {}
        ai_model = None
        if ai == "random":
            ai_model = CheckerModelRandom()
        elif ai == "minmax":
            ai_model = CheckerModelMinMax()
        elif ai == "mtc":
            ai_model = CheckerModelMTC()
        ai_model.move_piece(checker_model, **params)
