import random
import pygame
import numpy as np
import time


pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Sudoku Game")

# Colors
WHITE = pygame.Color("white")
BLACK = pygame.Color("black")
RED = pygame.Color("red")
BLUE = pygame.Color("blue")
GREEN = pygame.Color("green")
LIGHT_GRAY = pygame.Color("lightgray")
DARK_GRAY = pygame.Color("darkgray")

# Fonts
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
big_font = pygame.font.Font(None, 48)

# Global variables
grid = []
original_grid = []
solution_grid = []
selected_cell = None
incorrect_cells = set()
start_time = 0
hints_used = 0
max_hints = 3
game_won = False

def backgrnd():
    screen.fill(WHITE)
    # Main grid
    pygame.draw.rect(screen, BLACK, pygame.Rect(50, 50, 500, 500), 5)
    
    # Grid lines
    i = 1
    while (i * 55.56) < 500:
        if i % 3 == 0:#for every 3x3 box
            lw = 6
        else:
            lw = 3    
        pygame.draw.line(screen, BLACK, pygame.Vector2((i * 55.56)+50 , 50), pygame.Vector2((i * 55.56) + 50, 550), lw)#columns
        pygame.draw.line(screen, BLACK, pygame.Vector2(50, (i * 55.56)+50), pygame.Vector2(550, (i * 55.56) + 50), lw)#rows
        i += 1

def draw_numbers():
    global grid, original_grid, selected_cell, incorrect_cells
    
    for row in range(9):
        for col in range(9):
            x = 50 + col * 55.56 + 27.78
            y = 50 + row * 55.56 + 27.78
            
            # Highlight selected cell
            if selected_cell == (row, col):
                cell_rect = pygame.Rect(50 + col * 55.56 + 2, 50 + row * 55.56 + 2, 51.56, 51.56)
                pygame.draw.rect(screen, LIGHT_GRAY, cell_rect)
            
            # Draw cell background for incorrect cells
            if (row, col) in incorrect_cells:
                cell_rect = pygame.Rect(50 + col * 55.56 + 2, 50 + row * 55.56 + 2, 51.56, 51.56)
                pygame.draw.rect(screen, RED, cell_rect)
            
            # Draw numbers
            if grid[row][col] != 0:
                # Different colors for original and user-entered numbers
                if original_grid[row][col] != 0:
                    color = BLACK
                else:
                    color = BLUE
                
                text = font.render(str(grid[row][col]), True, color)
                text_rect = text.get_rect(center=(x, y))
                screen.blit(text, text_rect)

def draw_ui():
    global start_time, hints_used, max_hints, game_won
    
    # Timer
    if not game_won:
        elapsed = int(time.time() - start_time)
    else:
        elapsed = int(time.time() - start_time)
    
    minutes = elapsed // 60
    seconds = elapsed % 60
    timer_text = f"Time: {minutes:02d}:{seconds:02d}"
    timer_surface = small_font.render(timer_text, True, BLACK)
    screen.blit(timer_surface, (580, 50))
    
    # Hints counter
    hints_text = f"Hints: {hints_used}/{max_hints}"
    hints_surface = small_font.render(hints_text, True, BLACK)
    screen.blit(hints_surface, (580, 80))
    
    # Hint button display
    hint_button_rect = pygame.Rect(580, 110, 120, 40)
    if hints_used < max_hints and not game_won:
        button_color = GREEN
        text_color = BLACK
        button_text = "Get Hint"
    else:
        button_color = DARK_GRAY
        text_color = BLACK
        if hints_used >= max_hints:
            button_text = "No Hints Left"
        else:
            button_text = "Game Won!"
    
    pygame.draw.rect(screen, button_color, hint_button_rect)
    pygame.draw.rect(screen, BLACK, hint_button_rect, 2)
    
    hint_text_surface = small_font.render(button_text, True, text_color)
    hint_text_rect = hint_text_surface.get_rect(center=hint_button_rect.center)
    screen.blit(hint_text_surface, hint_text_rect)
    
    # Restart button
    restart_button_rect = pygame.Rect(580, 160, 120, 40)
    pygame.draw.rect(screen, BLUE, restart_button_rect)
    pygame.draw.rect(screen, BLACK, restart_button_rect, 2)
    
    restart_text_surface = small_font.render("Restart Game", True, WHITE)
    restart_text_rect = restart_text_surface.get_rect(center=restart_button_rect.center)
    screen.blit(restart_text_surface, restart_text_rect)
    
    # Instructions
    instructions = [
        "Controls:",
        "1-9: Enter number",
        "0: Clear cell",
        "Click cell to select"
    ]
    
    for i, instruction in enumerate(instructions):
        text_surface = small_font.render(instruction, True, BLACK)
        screen.blit(text_surface, (580, 220 + i * 25))
    
    # Win message
    if game_won:
        win_text = "Congratulations!"
        win_surface = big_font.render(win_text, True, GREEN)
        screen.blit(win_surface, (580, 350))
    
    return hint_button_rect, restart_button_rect

def get_cell_from_pos(pos):
    x, y = pos
    if 50 <= x <= 550 and 50 <= y <= 550:
        col = int((x - 50) // 55.56)
        row = int((y - 50) // 55.56)
        if 0 <= row < 9 and 0 <= col < 9:
            return (row, col)
    return None

def existsOrNot(grid, r, c, num):
    # Check row
    for i in range(9):
        if grid[r][i] == num:
            return False
    
    # Check column
    for i in range(9):
        if grid[i][c] == num:
            return False
    
    # Check 3x3 box
    r0 = (r // 3) * 3
    c0 = (c // 3) * 3
    
    for i in range(3):
        for j in range(3):
            if grid[r0 + i][c0 + j] == num:
                return False
    
    return True

def is_valid_move(row, col, num):
    if original_grid[row][col] != 0:  # Can't change original numbers
        return False
    
    # Check if the number violates Sudoku rules
    return existsOrNot(grid, row, col, num)

def check_win():
    # Check if all cells are filled and valid
    for row in range(9):
        for col in range(9):
            if grid[row][col] == 0:
                return False
    
    # Check if solution is correct
    for row in range(9):
        for col in range(9):
            if grid[row][col] != solution_grid[row][col]:
                return False
    
    return True

def get_hint():
    global hints_used, selected_cell
    
    if hints_used >= max_hints:
        return False
    

    if selected_cell is None:
        return False
    
    row, col = selected_cell
    if original_grid[row][col] != 0:  # Can't hint on original numbers
        return False
    
    # Only give hint if cell is empty or incorrect
    if grid[row][col] != 0 and grid[row][col] == solution_grid[row][col]:
        return False  # Already has correct answer
    
    grid[row][col] = solution_grid[row][col]
    hints_used += 1
    
    # Remove from incorrect cells if it was there
    if (row, col) in incorrect_cells:
        incorrect_cells.remove((row, col))
    
    return True

'''def get_random_hint():
    """Get a hint for any random empty cell"""
    global hints_used
    
    if hints_used >= max_hints:
        return False
    
    # Find all empty cells that are not original clues
    empty_cells = []
    for row in range(9):
        for col in range(9):
            if original_grid[row][col] == 0 and grid[row][col] == 0:
                empty_cells.append((row, col))
    
    # If no empty cells, try cells with wrong answers
    if not empty_cells:
        for row in range(9):
            for col in range(9):
                if (original_grid[row][col] == 0 and 
                    grid[row][col] != 0 and 
                    grid[row][col] != solution_grid[row][col]):
                    empty_cells.append((row, col))
    
    if not empty_cells:
        return False  # No cells need hints
    
    # Pick a random cell and give hint
    row, col = random.choice(empty_cells)
    grid[row][col] = solution_grid[row][col]
    hints_used += 1
    
    # Remove from incorrect cells if it was there
    if (row, col) in incorrect_cells:
        incorrect_cells.remove((row, col))
    
    # Update selected cell to show which cell got the hint
    global selected_cell
    selected_cell = (row, col)
    
    return True'''

def find_empty(grid):
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                return i, j
    return None

def solve_grid_randomized(grid):
    empty = find_empty(grid)
    if not empty:
        return True
    row, col = empty
    nums = list(range(1, 10))
    random.shuffle(nums)
    for num in nums:
        if existsOrNot(grid, row, col, num):
            grid[row][col] = num
            if solve_grid_randomized(grid):
                return True
            grid[row][col] = 0#backtracks it, it means puzzle does not get solved with the entered no. and so is set to 0 again
    return False

def generate_full_grid():
    grid = [[0 for _ in range(9)] for _ in range(9)]
    solve_grid_randomized(grid)
    return grid

def has_unique_solution(test_grid):
    count = [0]
    temp_grid = [row[:] for row in test_grid]

    def solve_and_count(grid):
        if count[0] > 1:
            return
        empty = find_empty(grid)
        if not empty:
            count[0] += 1
            return
        row, col = empty
        for num in range(1, 10):
            if existsOrNot(grid, row, col, num):
                grid[row][col] = num
                solve_and_count(grid)
                grid[row][col] = 0

    solve_and_count(temp_grid)
    return count[0] == 1

def remove_numbers(board, clues=40):
    attempts = 81 - clues
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)
    
    for row, col in cells:
        if attempts <= 0:
            break
        
        if board[row][col] == 0:
            continue
            
        temp = board[row][col]
        board[row][col] = 0
        
        if not has_unique_solution(board):
            board[row][col] = temp
        else:
            attempts -= 1
    
    return board

def generate_sudoku(clues=40):
    board = generate_full_grid()
    puzzle = [row[:] for row in board]  # Copy the solution
    remove_numbers(puzzle, clues)
    return puzzle, board

def restart_game():
    global grid, original_grid, solution_grid, selected_cell, incorrect_cells
    global start_time, hints_used, game_won
    
    grid, solution_grid = generate_sudoku(40)
    original_grid = [row[:] for row in grid]
    selected_cell = None
    incorrect_cells = set()
    start_time = time.time()
    hints_used = 0
    game_won = False

def game():
    global grid, original_grid, solution_grid, selected_cell, incorrect_cells
    global start_time, hints_used, game_won
    
    # Initialize game
    restart_game()
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check if hint button was clicked
                    hint_rect, restart_rect = draw_ui()
                    if hint_rect.collidepoint(event.pos):
                        if hints_used < max_hints and not game_won:
                            get_hint()
                            if check_win():
                                game_won = True
                    # Check if restart button was clicked
                    elif restart_rect.collidepoint(event.pos):
                        restart_game()
                    else:
                        # Select cell
                        selected_cell = get_cell_from_pos(event.pos)
            
            elif event.type == pygame.KEYDOWN:
                if selected_cell is not None and not game_won:
                    row, col = selected_cell
                    
                    # Number input (1-9)
                    if pygame.K_1 <= event.key <= pygame.K_9:
                        if original_grid[row][col] == 0:  # Only allow input on empty original cells
                            num = event.key - pygame.K_0
                            
                            # Remove from incorrect cells first
                            if (row, col) in incorrect_cells:
                                incorrect_cells.remove((row, col))
                            
                            # Check if the move is valid before placing
                            if is_valid_move(row, col, num):
                                grid[row][col] = num
                            else:
                                grid[row][col] = num
                                incorrect_cells.add((row, col))
                            
                            # Check for win condition
                            if check_win():
                                game_won = True
                    
                    # Clear cell (0 or Backspace)
                    elif event.key == pygame.K_0 or event.key == pygame.K_BACKSPACE:
                        if original_grid[row][col] == 0:  # Only allow clearing user-entered numbers
                            grid[row][col] = 0
                            if (row, col) in incorrect_cells:
                                incorrect_cells.remove((row, col))
                
                # Hint (H key)
                elif event.key == pygame.K_h and not game_won:
                    get_hint()
                    if check_win():
                        game_won = True
                
                # Restart (R key)
                elif event.key == pygame.K_r:
                    restart_game()
        
        # Draw everything
        backgrnd()
        draw_numbers()
        draw_ui()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    game()