import tqdm
import checker_model_ai as cm
import checker_model_ai as cmai

class BenchmarkAI:
    def __init__(self, player_configs=None, number_of_tests=50, checker_grid=None):
        if player_configs is None:
            player_configs = [
                ["random", {}],
                ["minmax", {"depth": 3, "to_maximize": False}]
            ]

        self.player_configs = player_configs
        self.number_of_tests = number_of_tests

    def play_game(self):
        wins_player_1 = 0
        wins_player_2 = 0
        player_configs = self.player_configs

        if len(player_configs) == 2:
            for _ in tqdm.tqdm(range(self.number_of_tests)):
                checker_model = cm.CheckerModel()
                checker_model_ai = cmai.CheckerModelAI()

                while True:
                    checker_model_ai.move_piece(checker_model, player_configs[0][0], **player_configs[0][1])
                    game_state = checker_model.check_game_state()

                    if game_state == "draw_game":
                        break
                    elif game_state == 1:
                        wins_player_1 += 1
                        break

                    checker_model_ai.move_piece(checker_model, player_configs[1][0], **player_configs[1][1])
                    game_state = checker_model.check_game_state()

                    if game_state == "draw_game":
                        break
                    elif game_state == -1:
                        wins_player_2 += 1
                        break

            print(f"Player 1: {player_configs[0][0]} wins {wins_player_1}")
            print(f"Player 2: {player_configs[1][0]} wins {wins_player_2}")
            print(f"Draws: {self.number_of_tests - wins_player_1 - wins_player_2}")
        else:
            print("We should only have 2 players!")

# Example usage of BenchmarkAI
benchmark_ai = BenchmarkAI(
    [
        ["mtc", {"depth": 3, "to_maximize": True, "nb_of_iterations": 5}],
        ["mtc", {"depth": 3, "to_maximize": False, "nb_of_iterations": 5}],
    ],
    number_of_tests=100
)

benchmark_ai.play_game()
