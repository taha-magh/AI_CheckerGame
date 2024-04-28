import random

class CheckerModelRandom:
    def __init__(self):
        pass

    def move_piece(self, checker_model, **params):
        selected_piece_position, move_position = self.get_random_move(checker_model)
        checker_model.move_piece(selected_piece_position, move_position)

    def get_random_move(self, checker_model):
        dict_of_moves = checker_model.dict_of_possible_moves
        list_of_moves = list(dict_of_moves.keys())
        selected_piece_position = random.choice(list_of_moves)
        selected_move = random.choice(dict_of_moves[selected_piece_position])

        move_position = selected_move.get_final_position()
        return selected_piece_position, move_position
