import random


class SudokuGame:
    def __init__(self):
        self.grid = [[0] * 9 for _ in range(9)]
        self.solutions = []
        self.is_unique = True

    def generate_puzzle(self, difficulty):
        """Generates a unique Sudoku puzzle of the specified difficulty"""

        self.generate_complete_grid()

        # Remove cells from grid to create the puzzle
        num_cells_to_remove = self.get_num_cells_to_remove(difficulty)
        cells_to_remove = random.sample(range(81), num_cells_to_remove)

        for cell_index in cells_to_remove:
            row = cell_index // 9
            col = cell_index % 9

            # Temporarily store the cell value before removing the cell
            removed_cell = self.grid[row][col]
            self.grid[row][col] = 0

            # Create a grid copy to check if the resulting puzzle has a unique solution
            grid_copy = [row[:] for row in self.grid]
            self.is_unique = True

            if self.solve_sudoku(grid_copy):
                if not self.is_unique:
                    # If current removed cell leads to a grid with more than one solution, put back
                    self.grid[row][col] = removed_cell

                    # remove the last stored solution to continue checking for uniqueness
                    self.solutions.pop()

        return self.grid

    def generate_complete_grid(self):
        """Generates a complete Sudoku grid using recursive backtracking"""

        def solve(grid, row, col):
            # Recursive function to fill the Sudoku grid until complete grid is generated

            if row == 9:  # Indicates end of grid
                return True

            next_row = row + 1 if col == 8 else row
            next_col = (col + 1) % 9

            for num in range(1, 10):
                if self.is_valid_move(grid, row, col, num):
                    grid[row][col] = num

                    if solve(grid, next_row, next_col):
                        return True

            grid[row][col] = 0  # Backtrack if no solution is found

            return False

        # Shuffle the numbers 1 to 9 for the first row to diversify results
        shuffled_numbers = random.sample(range(1, 10), 9)
        self.grid[0] = shuffled_numbers

        # Start solving the puzzle from the second row (1, 0)
        solve(self.grid, 1, 0)

    @staticmethod
    def get_num_cells_to_remove(difficulty):
        """Defines difficulty levels and corresponding number of cells to remove"""
        difficulty_levels = {
            "Easy": 35,
            "Medium": 45,
            "Expert": 54,
        }

        return difficulty_levels.get(difficulty)

    def solve_sudoku(self, grid):
        """Recursively solves sudoku grid"""

        grid = grid or self.grid

        # Find next empty cell
        empty_cell = self.find_empty_cell(grid)

        # If no more empty cells, puzzle is solved
        if not empty_cell:
            if grid not in self.solutions:
                self.solutions.append(grid)

            if len(self.solutions) > 1:  # Check for multiple solutions
                self.is_unique = False

            return True

        # Solve the puzzle by trying digits from 1 to 9 within the empty cells
        row, col = empty_cell

        for num in range(1, 10):
            if self.is_valid_move(grid, row, col, num):
                grid[row][col] = num

                if self.solve_sudoku(grid):
                    return True

        # If num recursively leads to dead-end, backtrack
        grid[row][col] = 0

        return False

    @staticmethod
    def find_empty_cell(grid):
        """Finds the next empty cell in the grid"""
        for row in range(9):
            for col in range(9):
                # Check for cells with notes, empty cells or wrongly filled cells
                if isinstance(grid[row][col], str):
                    return row, col
                elif grid[row][col] == 0 or grid[row][col] < 0:
                    return row, col
        return None

    @staticmethod
    def is_valid_move(grid, row, col, num):
        """Checks whether a digit placement violates any Sudoku rules"""

        # Check if num is already present in the same row
        if num in grid[row]:
            return False

        # Check if num is already present in the same column
        if num in [grid[i][col] for i in range(9)]:
            return False

        # Check if num is already present in the 3x3 subgrid
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(start_row, start_row + 3):
            for j in range(start_col, start_col + 3):
                if grid[i][j] == num:
                    return False

        return True

    def is_solved(self, grid):
        """Returns True if the final grid matches the unique solution, False otherwise"""
        return grid == self.solutions[0]
