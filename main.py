import sys
import pygame
from sudoku_gui import SudokuUI


def run(sudoku_ui):
    """Main game loop for event handling."""
    running = True
    showing_menu = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    mouse_cor = pygame.mouse.get_pos()

                    if showing_menu:
                        if sudoku_ui.difficulty_selected(mouse_cor):
                            showing_menu = False
                            sudoku_ui.start_new_game(sudoku_ui.difficulty)

                    else:
                        # Handle events while game is in progress
                        if sudoku_ui.new_game_clicked(mouse_cor):
                            showing_menu = True

                        else:
                            sudoku_ui.selected_cell = sudoku_ui.get_clicked_cell(
                                mouse_cor
                            )

                            if sudoku_ui.highlighted_cell:
                                row, col = sudoku_ui.highlighted_cell

                                # Get screen button clicks

                                num_clicked = sudoku_ui.num_button_clicked(mouse_cor)
                                if num_clicked:
                                    # Check if cell is modifiable: empty or contains notes
                                    if sudoku_ui.grid[row][col] == 0 or isinstance(
                                        sudoku_ui.grid[row][col], str
                                    ):
                                        sudoku_ui.handle_num_input(
                                            row, col, num_clicked
                                        )

                                sudoku_ui.del_button_clicked(row, col, mouse_cor)

                                sudoku_ui.notes_button_clicked(mouse_cor)

                            sudoku_ui.solve_button_clicked(mouse_cor)

            elif event.type == pygame.KEYDOWN:
                if sudoku_ui.highlighted_cell:
                    row, col = sudoku_ui.highlighted_cell
                    key = event.unicode

                    # Check if entered key is a valid digit and selected cell is empty / contains notes
                    if (key.isdigit() and 1 <= int(key) <= 9) and (
                        sudoku_ui.grid[row][col] == 0 or sudoku_ui.notes_mode
                    ):
                        sudoku_ui.handle_num_input(row, col, int(key))

                    # Delete entry
                    elif event.key == pygame.K_BACKSPACE:
                        if sudoku_ui.sudoku_board[row][col] == 0:
                            sudoku_ui.grid[row][col] = 0

        # Display Game menu / Sudoku Board
        if showing_menu:
            sudoku_ui.game_menu()
        elif not sudoku_ui.freeze_screen:
            sudoku_ui.draw_grid(sudoku_ui.grid)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    game_ui = SudokuUI()
    run(game_ui)
