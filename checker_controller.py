import pygame
import checker_model_ai
import checker_view
import checker_model_ai
from config_file import *

class CheckerController:
    def __init__(self, checker_grid):
        self.checker_model_object = checker_model_ai.CheckerModel(checker_grid)
        self.checker_model_ai = checker_model_ai.CheckerModelAI()
        self.checker_view_object = checker_view.CheckerView()
        self.run_game()

    def selected_piece(self, x, y):
        selected_piece = checker_view.CheckerView.compute_row_col_of_selected_piece(x, y)
        possible_moves_positions = []

        if selected_piece in self.checker_model_object.dict_of_possible_moves.keys():
            possible_moves_positions = [move_object.get_final_position() for move_object in self.checker_model_object.dict_of_possible_moves[selected_piece]]

        return selected_piece, possible_moves_positions

    def action_on_grid(self, selected_piece, possible_moves_positions, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked_position = pygame.mouse.get_pos()

            if not selected_piece or not possible_moves_positions:
                selected_piece, possible_moves_positions = self.selected_piece(*clicked_position)

            elif selected_piece and possible_moves_positions:
                move = checker_view.CheckerView.compute_row_col_of_selected_piece(*clicked_position)

                if move in possible_moves_positions:
                    self.checker_model_object.move_piece(selected_piece, move)
                    selected_piece = None
                    possible_moves_positions = []

        return selected_piece, possible_moves_positions

    def undo_action(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.Rect(*UNDO_BUTTON_POSITION, *BUTTON_SIZE).collidepoint(event.pos):
            self.checker_model_object.undo_last_action()

    def run_game(self):
        run = True
        clock = pygame.time.Clock()
        selected_piece = None
        possible_moves_positions = []
        player = 1

        while run:
            clock.tick(FPS)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if player == 1:
                    selected_piece, possible_moves_positions = self.action_on_grid(selected_piece, possible_moves_positions, event)
                    self.undo_action(event)

            # AI's turn
            if player == 2:
                if self.checker_model_object.is_game_over():
                    print("AI won")
                    run = False
                else:
                    # Perform AI move
                    self.checker_model_ai.move_piece(self.checker_model_object, "minmax")
                    player = 1

            # Update view
            self.checker_view_object.update_grid(self.checker_model_object.checker_grid)
            pygame.display.update()

        pygame.quit()

# Configure FPS and button positions here
FPS = 60
BUTTON_SIZE = (100, 50)
UNDO_BUTTON_POSITION = (10, 10)
