import random
from config_file import *
from piece import Piece
import tqdm


class CheckerModelMinMax:
    def __init__(self):
        pass

    def move_piece(self, checker_model, search_depth=3, maximize_score=False):
        best_piece_pos, best_move_pos = self.get_best_move(checker_model, search_depth, maximize_score=maximize_score)
        checker_model.move_piece(best_piece_pos, best_move_pos)

    def get_best_move(self, checker_model, search_depth, maximize_score=False):
        best_score = -float("inf") if maximize_score else float("inf")
        best_piece_pos, best_move_pos = None, None
        moves_dict = checker_model.dict_of_possible_moves

        possible_actions = []
        for piece_pos, moves in moves_dict.items():
            for move in moves:
                possible_actions.append((piece_pos, move.get_final_position()))

        for action in possible_actions:
            checker_model.move_piece(*action)
            score = self.minimax(checker_model, robot_turn=False, depth=search_depth, maximize_score=maximize_score)

            if maximize_score:
                if score >= best_score:
                    best_score = score
                    best_piece_pos, best_move_pos = action
            else:
                if score <= best_score:
                    best_score = score
                    best_piece_pos, best_move_pos = action

            checker_model.undo_last_action()

        return best_piece_pos, best_move_pos

    def minimax(self, checker_model, robot_turn, depth=3, alpha=-float('inf'), beta=float('inf'), maximize_score=False):
        game_state = checker_model.check_game_state()

        if game_state == "draw_game":
            return 0
        elif game_state == 1:
            return float("inf")
        elif game_state == -1:
            return -float("inf")
        elif game_state == "game_in_progress":
            grid_state = checker_model.checker_grid

            if depth == 0:
                return checker_model.evaluate_grid(checker_model.checker_grid)
            else:
                if maximize_score:
                    best_score = -float('inf') if robot_turn else float('inf')
                else:
                    best_score = float('inf') if robot_turn else -float('inf')

                moves_dict = checker_model.dict_of_possible_moves
                possible_actions = []

                for piece_pos, moves in moves_dict.items():
                    for move in moves:
                        possible_actions.append((piece_pos, move.get_final_position()))

                for action in possible_actions:
                    piece_pos = action[0]

                    if type(grid_state[piece_pos[0]][piece_pos[1]]) is Piece:
                        checker_model.move_piece(*action)
                        score = self.minimax(checker_model, robot_turn=not robot_turn, depth=depth - 1,
                                            alpha=alpha, beta=beta, maximize_score=maximize_score)
                        checker_model.undo_last_action()

                        if maximize_score:
                            best_score = max(score, best_score) if robot_turn else min(score, best_score)
                        else:
                            best_score = min(score, best_score) if robot_turn else max(score, best_score)

                        if maximize_score and robot_turn or not (maximize_score or robot_turn):
                            if best_score > beta:
                                break
                            alpha = max(beta, best_score)
                        elif maximize_score and not robot_turn or not (maximize_score and not robot_turn):
                            if alpha > best_score:
                                break
                            beta = min(alpha, best_score)

                return best_score
