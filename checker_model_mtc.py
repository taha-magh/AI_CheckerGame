import random
from config_file import *
from piece import Piece
import tqdm


class CheckerModelMTC:
    def __init__(self):
        pass

    def move_piece(self, checker_model, depth=3, maximize=False, iterations=5):
        selected_piece_position, move_position = self.get_best_move(checker_model, depth, maximize=maximize, iterations=iterations)
        checker_model.move_piece(selected_piece_position, move_position)

    def get_random_move(self, possible_actions):
        return random.choice(possible_actions)

    def get_best_move(self, checker_model, depth, maximize=False, iterations=5):
        best_score = -float("inf") if maximize else float("inf")
        best_piece_position, best_move_position = None, None
        dict_of_moves = checker_model.dict_of_possible_moves

        # possible_actions = [( (piece) : (move) ),]
        possible_actions = []
        for selected_piece_position, moves in dict_of_moves.items():
            for move in moves:
                possible_actions.append((selected_piece_position, move.get_final_position()))

        # for possible_action in possible_actions:
        for _ in range(iterations):
            possible_action = self.get_random_move(possible_actions)
            checker_model.move_piece(*possible_action)
            score = self.minimax(checker_model=checker_model, robot_turn=False, depth=depth, maximize=maximize, iterations=iterations)

            if maximize:
                # we are looking for max
                if score >= best_score:
                    best_score = score
                    best_piece_position, best_move_position = possible_action
            else:
                # we are looking for min
                if score <= best_score:
                    best_score = score
                    best_piece_position, best_move_position = possible_action

            checker_model.undo_last_action()

        return best_piece_position, best_move_position

    def minimax(self, checker_model, robot_turn, depth=3, alpha=-float('inf'), beta=float('inf'), maximize=False, iterations=5):
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
                if maximize:
                    best_score = -float('inf') if robot_turn else float('inf')
                else:
                    best_score = float('inf') if robot_turn else -float('inf')

                dict_of_moves = checker_model.dict_of_possible_moves

                # possible_actions = [( (piece) : (move) ),]
                possible_actions = []
                for selected_piece_position, moves in dict_of_moves.items():
                    for move in moves:
                        possible_actions.append((selected_piece_position, move.get_final_position()))

                for _ in range(iterations):
                    possible_action = self.get_random_move(possible_actions)
                    piece_position = possible_action[0]
                    if type(grid_state[piece_position[0]][piece_position[1]]) is Piece:
                        checker_model.move_piece(*possible_action)
                        score = self.minimax(checker_model=checker_model, robot_turn=not robot_turn, depth=depth - 1,
                                            alpha=alpha, beta=beta, maximize=maximize, iterations=iterations)
                        checker_model.undo_last_action()

                        if maximize:
                            best_score = max(score, best_score) if robot_turn else min(score, best_score)
                        else:
                            best_score = min(score, best_score) if robot_turn else max(score, best_score)

                        if maximize and robot_turn or not (maximize or robot_turn):
                            if best_score > beta:
                                break
                            alpha = max(beta, best_score)
                        elif maximize and not robot_turn or not (maximize and not robot_turn):
                            if alpha > best_score:
                                break
                            beta = min(alpha, best_score)

                return best_score
