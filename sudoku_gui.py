import copy
import pygame
from sudoku_game_logic import SudokuGame


class SudokuUI:
    def __init__(self):
        self.WINDOW_SIZE = (720, 790)
        self.MARGIN = 90
        self.CELL_SIZE = 60
        self.WINDOW_BG_COLOR = '#F7F7E8'

        self.new_game_rect = pygame.Rect(530, 5, 100, 30)
        self.menu_buttons = {}
        self.num_button_rects = []
        self.solve_button_rect = pygame.Rect(90, 50, 80, 35)
        self.del_button_rect = pygame.Rect(380, 710, 70, 30)
        self.notes_button_rect = pygame.Rect(290, 710, 70, 30)
        self.notes_mode = False
        self.note_colors = ['#00BCD4', '#388E3C', '#4E342E', '#7986CB', '#C0CA33', '#827717', '#757575', '#424242',
                            '#009688']

        # Set up Pygame
        pygame.init()
        self.screen = pygame.display.set_mode(self.WINDOW_SIZE)
        pygame.display.set_caption("Sudoku Arcade")
        self.clock = pygame.time.Clock()
        self.start_time = pygame.time.get_ticks()
        self.end_time = None

        # Initialize game logic
        self.game = SudokuGame()
        self.difficulty = None

        # Sudoku Board Parameters
        self.sudoku_board = None
        self.grid = None
        self.font = pygame.font.Font('fonts/Anta-Regular.ttf', 25)
        self.selected_cell = None
        self.highlighted_cell = None
        self.current_lives = 4
        self.max_lives = 4
        self.auto_solve = False
        self.game_won = False
        self.game_end = False
        self.freeze_screen = False

    def game_menu(self):
        """Renders the game menu UI"""
        background = pygame.Rect(0, 0, self.WINDOW_SIZE[0], self.WINDOW_SIZE[1])
        pygame.draw.rect(self.screen, self.WINDOW_BG_COLOR, background)

        font = pygame.font.Font('fonts/PressStart2P-Regular.ttf', 40)
        text_surface = font.render('SUDOKU ARCADE', True, '#827717')
        text_rect = text_surface.get_rect(center=(360, 200))
        self.screen.blit(text_surface, text_rect)

        font = pygame.font.Font('fonts/Anta-Regular.ttf', 20)
        text_surface = font.render('Choose Difficulty', True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(360, 265))
        self.screen.blit(text_surface, text_rect)

        easy_btn = pygame.Rect(285, 290, 150, 30)
        medium_btn = pygame.Rect(285, 330, 150, 30)
        expert_btn = pygame.Rect(285, 370, 150, 30)
        self.menu_buttons = {'Easy': easy_btn, 'Medium': medium_btn, 'Expert': expert_btn}
        for text, button in self.menu_buttons.items():
            pygame.draw.rect(self.screen, '#FBECB2', button)
            pygame.draw.rect(self.screen, '#45474B', button, 3)
            font = pygame.font.Font('fonts/Anta-Regular.ttf', 18)
            text_surface = font.render(text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=button.center)
            self.screen.blit(text_surface, text_rect)

    def draw_grid(self, grid):
        """Draws Sudoku Grid"""
        self.screen.fill(self.WINDOW_BG_COLOR)

        # Draw grid cells
        for i in range(9):
            for j in range(9):
                x0 = self.MARGIN + j * self.CELL_SIZE
                y0 = self.MARGIN + i * self.CELL_SIZE
                width = height = self.CELL_SIZE
                grid_ln_color = '#7B8F7A'

                # Draw non-zero numbers within cells
                if grid[i][j] != 0:
                    if isinstance(grid[i][j], str):  # check if cell contains notes
                        self.draw_notes(grid[i][j], x0, y0, width, height)
                    else:
                        # Set background color based on the cell value; even or odd
                        even_color = '#9DAD7F'
                        odd_color = '#C7CFB7'
                        cell_bg_color = even_color if grid[i][j] % 2 == 0 else odd_color

                        pygame.draw.rect(self.screen, cell_bg_color, (x0, y0, width, height))

                        # Set text color: black for original numbers, red for invalid inputs, and blue for valid inputs
                        text_color = 'black' if self.sudoku_board[i][j] != 0 else (
                            'red' if grid[i][j] < 0 else '#176CF0')

                        # Convert negative value (wrong entry) to positive for rendering
                        num = abs(grid[i][j])

                        # Render value within cells
                        text = self.font.render(str(num), True, text_color)
                        text_rect = text.get_rect(center=(x0 + width // 2, y0 + height // 2))
                        self.screen.blit(text, text_rect)

                # Draw grid lines
                pygame.draw.rect(self.screen, grid_ln_color, (x0, y0, width, height), 1)

        # Draw thicker grid lines
        for i in range(9):
            for j in range(9):
                x0 = self.MARGIN + j * self.CELL_SIZE
                y0 = self.MARGIN + i * self.CELL_SIZE
                width = height = self.CELL_SIZE
                subgrid_ln_color = '#12372A'
                highlight_color = '#FFAB40'

                if i % 3 == 0 and j % 3 == 0:
                    pygame.draw.rect(self.screen, subgrid_ln_color,
                                     (x0 - 1, y0 - 1, self.CELL_SIZE * 3 + 2, self.CELL_SIZE * 3 + 2), 3)

                # Highlight selected cell
                if self.selected_cell == (i, j):
                    pygame.draw.rect(self.screen, highlight_color, (x0, y0, width, height), 3)
                    self.highlighted_cell = self.selected_cell

        # Keep highlight on selected cell when another button is clicked
        if self.selected_cell is None:
            if self.highlighted_cell:
                row, col = self.highlighted_cell
                x0 = self.MARGIN + col * self.CELL_SIZE
                y0 = self.MARGIN + row * self.CELL_SIZE
                pygame.draw.rect(self.screen, '#FFAB40', (x0, y0, self.CELL_SIZE, self.CELL_SIZE), 3)

        self.draw_lives()
        self.update_clock()
        self.draw_new_game_button()
        self.draw_solve_button()
        self.draw_num_buttons()
        self.draw_notes_button()
        self.draw_delete_button()

        # Display results at game end
        if self.game_end:
            self.display_results()
            self.freeze_screen = True

    def draw_new_game_button(self):
        button_text = 'New Game'
        button_color = '#FBECB2'

        # Draw button and border
        pygame.draw.rect(self.screen, button_color, self.new_game_rect)
        pygame.draw.rect(self.screen, '#45474B', self.new_game_rect, 3)

        # Draw the text on the button
        font = pygame.font.Font('fonts/Anta-Regular.ttf', 18)
        text_surface = font.render(button_text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.new_game_rect.center)
        self.screen.blit(text_surface, text_rect)

        # Display text for game difficulty at the top
        text_surface = font.render(self.difficulty, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(360, 25))
        self.screen.blit(text_surface, text_rect)

    def draw_solve_button(self):
        button_text = 'solve'
        button_color = '#31A52C'

        pygame.draw.rect(self.screen, button_color, self.solve_button_rect,
                         border_radius=7)
        pygame.draw.rect(self.screen, '#12372A', self.solve_button_rect, border_radius=7, width=3)

        font = pygame.font.Font('fonts/Anta-Regular.ttf', 25)
        text_surface = font.render(button_text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.solve_button_rect.center)
        self.screen.blit(text_surface, text_rect)

    def draw_lives(self):
        """Displays player's remaining lives"""
        circle_radius = 8
        circle_color = '#00838F'

        # Calculate the horizontal offset to center the circles
        total_width = 4 * 2.5 * circle_radius
        horizontal_offset = (self.WINDOW_SIZE[0] - total_width) // 2

        for i in range(self.max_lives):
            x = horizontal_offset + (i * 2.5 * circle_radius) + circle_radius
            y = self.MARGIN - 20

            # Set circle color based on remaining lives
            circle_color = circle_color if i < self.current_lives else '#B4B4B8'

            pygame.draw.circle(self.screen, circle_color, (x, y), circle_radius)

    def draw_num_buttons(self):
        """Draws clickable numbers for entering values into grid"""
        button_color = '#C7CFB7'
        text_color = '#263238'

        for num in range(1, 10):
            x0 = self.MARGIN + num * 0.86 * self.CELL_SIZE
            y0 = self.WINDOW_SIZE[1] - 130

            button_rect = pygame.Rect(x0, y0, 30, 30)
            self.num_button_rects.append(button_rect)

            pygame.draw.rect(self.screen, button_color, button_rect, border_radius=3)

            button_text = str(num)
            font = pygame.font.Font('fonts/Anta-Regular.ttf', 15)
            text_surface = font.render(button_text, True, text_color)
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)

    def draw_notes_button(self):
        button_color = '#009688' if self.notes_mode else '#C7CFB7'
        text_color = '#263238'

        pygame.draw.rect(self.screen, button_color, self.notes_button_rect)
        pygame.draw.rect(self.screen, '#757575', self.notes_button_rect, width=3)

        font = pygame.font.Font('fonts/Anta-Regular.ttf', 18)
        text_surface = font.render('notes', True, text_color)
        text_rect = text_surface.get_rect(center=self.notes_button_rect.center)
        self.screen.blit(text_surface, text_rect)

    def draw_delete_button(self):
        pygame.draw.rect(self.screen, '#C7CFB7', self.del_button_rect)
        pygame.draw.rect(self.screen, '#757575', self.del_button_rect, width=3)
        font = pygame.font.Font('fonts/Anta-Regular.ttf', 18)
        text_surface = font.render('Delete', True, '#263238')
        text_rect = text_surface.get_rect(center=self.del_button_rect.center)
        self.screen.blit(text_surface, text_rect)

    def draw_notes(self, notes_str, x0, y0, cell_width, cell_height):
        """Arranges notes at specific positions within a cell"""
        cell_margin = 5

        # Create 3x3 grid for arranging notes within the cell
        num_rows = 3
        num_cols = 3

        # Calculate spacing for each row and column
        row_spacing = (cell_height - cell_margin * 2) // num_rows
        col_spacing = (cell_width - cell_margin * 2) // num_cols

        # Map note numbers to their fixed positions within the cell
        note_positions = {
            1: (0, 0),
            2: (0, 1),
            3: (0, 2),
            4: (1, 0),
            5: (1, 1),
            6: (1, 2),
            7: (2, 0),
            8: (2, 1),
            9: (2, 2),
        }

        # Iterate through notes string, converting to integers
        for i, char in enumerate(notes_str):
            note_num = int(char)

            # Get the designated position for the note
            row, col = note_positions[note_num]

            # Calculate x, y coordinates based on designated position
            note_x = x0 + cell_margin + col * col_spacing + 9
            note_y = y0 + cell_margin + row * row_spacing + 9

            # Render and draw note text with specified color
            font = pygame.font.Font('fonts/Anta-Regular.ttf', 16)
            note_text = font.render(str(note_num), True, self.note_colors[note_num - 1])
            note_rect = note_text.get_rect(center=(note_x, note_y))
            self.screen.blit(note_text, note_rect)

    def update_clock(self):
        """Displays elapsed time during game"""
        if not self.game_end:
            elapsed_time = pygame.time.get_ticks() - self.start_time
        else:
            elapsed_time = self.end_time - self.start_time

        minutes = elapsed_time // 60000
        seconds = (elapsed_time // 1000) % 60

        time_str = f"{minutes:02d}:{seconds:02d}"

        text_surface = self.font.render(time_str, True, (0, 0, 0))
        text_rect = text_surface.get_rect(topright=(self.WINDOW_SIZE[0] - self.MARGIN, 60))
        self.screen.blit(text_surface, text_rect)

    def display_results(self):
        """Displays game results"""
        display_msg = 'Game won!' if self.game_won else 'Game over.'

        if self.auto_solve:
            display_msg = "Sudoku solved!"

        text_surface = self.font.render(display_msg, True, 'black')
        text_rect = text_surface.get_rect(center=(350, 355))

        padding_x = 10
        padding_y = 5
        text_rect.width += 2 * padding_x
        text_rect.height += 2 * padding_y

        pygame.draw.rect(self.screen, '#FBECB2', text_rect)
        pygame.draw.rect(self.screen, '#45474B', text_rect, 3)

        text_rect.x += padding_x
        text_rect.y += padding_y
        self.screen.blit(text_surface, text_rect)

    def get_clicked_cell(self, mouse_cor):
        """Converts mouse position to grid cell indices"""
        x, y = mouse_cor
        if (self.MARGIN < x < self.WINDOW_SIZE[0] - self.MARGIN) and (self.MARGIN < y < self.WINDOW_SIZE[1] - 160):
            row = (y - self.MARGIN) // self.CELL_SIZE
            col = (x - self.MARGIN) // self.CELL_SIZE
            return row, col

    def num_button_clicked(self, mouse_cor):
        """Detects clicks on the on-screen num buttons"""
        if self.highlighted_cell:
            for num in range(1, 10):
                if self.num_button_rects[num - 1].collidepoint(mouse_cor):
                    return num

    def notes_button_clicked(self, mouse_cor):
        """Toggles notes mode on or off"""
        if self.notes_button_rect.collidepoint(mouse_cor):
            self.notes_mode = not self.notes_mode
            return True

    def del_button_clicked(self, row, col, mouse_cor):
        """Detects click of delete button"""
        if self.del_button_rect.collidepoint(mouse_cor):
            if self.sudoku_board[row][col] == 0:
                self.grid[row][col] = 0

    def solve_button_clicked(self, mouse_cor):
        """Detects solve button click and calls solve method"""
        if not self.freeze_screen:
            if self.solve_button_rect.collidepoint(mouse_cor):
                self.solve_sudoku_board(self.grid)

    def new_game_clicked(self, mouse_cor):
        if self.new_game_rect.collidepoint(mouse_cor):
            return True

    def difficulty_selected(self, mouse_cor):
        """Detects the difficulty selected from menu buttons"""
        for difficulty in self.menu_buttons:
            if self.menu_buttons[difficulty].collidepoint(mouse_cor):
                self.difficulty = difficulty
                return True

    def solve_sudoku_board(self, grid):
        """Solves sudoku board when the solve_button is clicked."""
        self.selected_cell = self.highlighted_cell = None

        empty_cell = self.game.find_empty_cell(grid)

        if not empty_cell:
            self.auto_solve = True
            self.game_end = True
            self.end_time = pygame.time.get_ticks()
            return True

        row, col = empty_cell

        grid[row][col] = self.game.solutions[0][row][col]

        self.draw_grid(grid)
        pygame.display.flip()
        pygame.time.wait(20)

        self.solve_sudoku_board(grid)

    def wrong_entry(self):
        """Deducts a life when the user makes a wrong entry"""
        self.current_lives -= 1
        if self.current_lives <= 0:
            self.game_end = True
            self.end_time = pygame.time.get_ticks()

    def handle_num_input(self, row, col, num):
        """Validates num inputs and stores note inputs as strings"""
        if self.notes_mode:
            if isinstance(self.grid[row][col], str):  # Check if cell already has notes i.e. is str type
                if str(num) not in self.grid[row][col]:
                    self.grid[row][col] += str(num)
                else:
                    # Delete existing note if same note is clicked again
                    self.grid[row][col] = self.grid[row][col].replace(str(num), '')
            else:
                # If empty cell, just add note
                self.grid[row][col] = str(num)

        else:
            # Validate num inputs with solution grid
            if num == self.game.solutions[0][row][col]:
                self.grid[row][col] = num
            else:
                self.grid[row][col] = -num
                self.wrong_entry()

            if self.game.is_solved(self.grid):
                self.game_won = True
                self.game_end = True
                self.end_time = pygame.time.get_ticks()
                self.display_results()

    def start_new_game(self, difficulty):
        """Resets instance attributes and initializes new game"""
        self.difficulty = difficulty
        self.start_time = pygame.time.get_ticks()
        self.end_time = None
        self.current_lives = 4
        self.game_end = False
        self.game_won = False
        self.auto_solve = False
        self.notes_mode = False
        self.freeze_screen = False
        self.selected_cell = False

        # Generate new Sudoku puzzle
        self.game = SudokuGame()
        self.sudoku_board = self.game.generate_puzzle(self.difficulty)
        self.grid = copy.deepcopy(self.sudoku_board)
