import random
import numpy as np
import math
import copy
from itertools import product

from move import Move
from piece import Piece
from utils import is_in_bound

class CheckerModel:
    def __init__(self, checker_grid=None):
        if checker_grid is None:
            self.create_grid()
        else:
            self.checker_grid = checker_grid
        self.current_player = 1  # 1 for player 1 and -1 for player 2

        self.possible_moves = self.get_possible_moves()
        self.history = []

    def create_grid(self):
        self.checker_grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

        for row in range(ROWS):
            for col in range(COLS):
                if (row + col) % 2 == 0:
                    self.checker_grid[row][col] = math.nan

        for row in range(ROWS):
            for col in range(COLS):
                if (row + col) % 2 != 0:
                    if row < FILLED_ROWS:
                        self.checker_grid[row][col] = Piece(row, col, player=-1)  # player 2
                    elif row > ROWS - FILLED_ROWS - 1:
                        self.checker_grid[row][col] = Piece(row, col, player=1)  # player 1

    def move_piece(self, selected_piece_position, move_position):
        self.history.append(copy.deepcopy(self.checker_grid))

        row_sel, col_sel = selected_piece_position
        current_piece = self.checker_grid[row_sel][col_sel]

        current_piece.row, current_piece.col = move_position

        if (self.current_player == 1 and current_piece.row == 0) or (self.current_player == -1 and current_piece.row == ROWS - 1):
            current_piece.become_king()

        self.checker_grid[row_sel][col_sel] = 0
        self.checker_grid[current_piece.row][current_piece.col] = current_piece

        for move_obj in self.possible_moves[selected_piece_position]:
            if move_obj.get_final_position() == move_position:
                for enemy_pos in move_obj.list_attacked_enemy_pieces:
                    row_att, col_att = enemy_pos
                    self.checker_grid[row_att][col_att] = 0

        self.current_player = -self.current_player
        self.possible_moves = self.get_possible_moves()

    def undo_last_action(self):
        if self.history:
            self.checker_grid = self.history[-1]
            self.history = self.history[:-1]
            self.current_player = -self.current_player
            self.possible_moves = self.get_possible_moves()

    def get_cell_state(self, row, col):
        if not is_in_bound(row, col):
            return "out_of_bound"

        elif self.checker_grid[row][col] == 0:
            return "accessible"

        elif type(self.checker_grid[row][col]) == Piece:
            piece = self.checker_grid[row][col]

            if piece.player == self.current_player:
                return "not_accessible"

            else:
                return "enemy"

    def get_possible_moves(self):
        dict_of_all_moves = {}

        for row, col in product(range(ROWS), range(COLS)):
            if type(self.checker_grid[row][col]) == Piece:
                current_piece = self.checker_grid[row][col]

                if current_piece.player == self.current_player:
                    depth, all_moves = self.get_possible_moves_for_piece(current_piece, depth=0, all_moves=[])

                    if all_moves:
                        dict_of_all_moves[(row, col)] = depth, all_moves

        possible_moves = {}
        max_depth = 0

        for piece, (depth, moves) in dict_of_all_moves.items():
            if moves:
                if depth > max_depth:
                    max_depth = depth
                    possible_moves = {piece: moves}

                elif depth == max_depth:
                    possible_moves[piece] = moves

        return possible_moves

    def get_possible_moves_for_piece(self, piece, depth, all_moves):
        row, col = piece.row, piece.col
        cells_to_check = piece.get_cells_to_check()

        for row_to_check, col_to_check in cells_to_check:
            stop_verify = False

            for row_to_verify in range(row, row_to_check, 1 if row_to_check > row else -1):
                for col_to_verify in range(col, col_to_check, 1 if col_to_check > col else -1):
                    if type(self.checker_grid[row_to_verify][col_to_verify]) == Piece and (row_to_verify != row and col_to_verify != col):
                        stop_verify = True

            if not stop_verify:
                cell_state = self.get_cell_state(row_to_check, col_to_check)

                if cell_state == "accessible" and depth == 0 and (row_to_check - row != self.current_player or piece.king):
                    move_obj = Move(initial_piece_position=(row, col), list_piece_positions=[(row_to_check, col_to_check)], list_attacked_enemy_pieces=[])
                    all_moves.append(move_obj)

                elif cell_state == "enemy":
                    row_arrival = row_to_check + 1 if row_to_check > row else row_to_check - 1
                    col_arrival = col_to_check + 1 if col_to_check > col else col_to_check - 1

                    if self.get_cell_state(row_arrival, col_arrival) == "accessible":
                        attacked_piece = self.checker_grid[row_to_check][col_to_check]

                        self.checker_grid[row][col] = 0
                        self.checker_grid[row_to_check][col_to_check] = 0
                        self.checker_grid[row_arrival][col_arrival] = piece
                        piece.row, piece.col = row_arrival, col_arrival

                        if depth == 0:
                            move_obj = Move(initial_piece_position=(row, col), list_piece_positions=[(row_arrival, col_arrival)], list_attacked_enemy_pieces=[(row_to_check, col_to_check)])
                            all_moves.append(move_obj)

                        else:
                            if depth <= all_moves[-1].get_depth():
                                current_move = all_moves[-1].extract_common_deplacement(extraction_depth=depth)
                                all_moves.append(current_move)

                            all_moves[-1].update_move(new_piece_position=(row_arrival, col_arrival), new_attacked_enemy_piece=(row_to_check, col_to_check))

                        self.get_possible_moves_for_piece(piece, depth + 1, all_moves)

                        piece.row, piece.col = row, col
                        self.checker_grid[row][col] = piece
                        self.checker_grid[row_to_check][col_to_check] = attacked_piece
                        self.checker_grid[row_arrival][col_arrival] = 0

        max_depth = 0
        possible_moves = []

        for move in all_moves:
            move_depth = move.get_depth()

            if move_depth > max_depth:
                max_depth = move_depth
                possible_moves = [move]

            elif move_depth == max_depth:
                possible_moves.append(move)

        return max_depth, possible_moves

    @staticmethod
    def evaluate_grid(checker_grid, king_value=5):
        score = 0

        for row in range(ROWS):
            for col in range(COLS):
                if type(checker_grid[row][col]) is Piece:
                    current_piece = checker_grid[row][col]
                    score += current_piece.player * (king_value if current_piece.king else 1)

        return score

    def check_game_state(self):
        if len(self.history) >= 15:
            draw_game = True
            game_eval = self.evaluate_grid(self.history[-25:])

            for checker_grid in self.history[-24:]:
                if self.evaluate_grid(checker_grid) != game_eval:
                    draw_game = False

            if draw_game:
                return "draw_game"

        if not self.possible_moves.keys():
            return 1 if self.current_player == -1 else -1

        else:
            return "game_in_progress"
