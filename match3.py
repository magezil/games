import random
import sys
import pygame

#!/usr/bin/env python3
"""
Simple Match-3 game with point-and-click interface using Pygame.
Save as /home/calamansi/red_car_game/match3.py and run with Python 3.

Controls:
 - Click on two adjacent gems to swap them
 - Close window to quit
"""

# Initialize Pygame
pygame.init()

# Constants
CELL_SIZE = 60
GEMS = ['A', 'B', 'C', 'D', 'E', 'F']
COLORS = {
    'A': (255, 0, 0),    # Red
    'B': (0, 255, 0),    # Green
    'C': (0, 0, 255),    # Blue
    'D': (255, 255, 0),  # Yellow
    'E': (255, 0, 255),  # Magenta
    'F': (0, 255, 255)   # Cyan
}


class Board:
    def __init__(self, rows=8, cols=8, gem_types=6):
        self.rows = rows
        self.cols = cols
        self.gem_types = max(3, min(gem_types, len(GEMS)))
        self.grid = [[None] * cols for _ in range(rows)]
        self.score = 0
        self.screen = pygame.display.set_mode((cols * CELL_SIZE, rows * CELL_SIZE))
        pygame.display.set_caption("Match-3 Game")
        self.selected = None
        self.fill_initial()

    def random_gem(self):
        return GEMS[random.randrange(self.gem_types)]

    def fill_initial(self):
        # Fill board avoiding initial matches
        for r in range(self.rows):
            for c in range(self.cols):
                while True:
                    self.grid[r][c] = self.random_gem()
                    if not self._creates_match_at(r, c):
                        break

    def _creates_match_at(self, r, c):
        v = self.grid[r][c]
        # check horizontal
        count = 1
        for dc in (1, 2):
            cc = c - dc
            if cc >= 0 and self.grid[r][cc] == v:
                count += 1
            else:
                break
        if count >= 3:
            return True
        # check vertical
        count = 1
        for dr in (1, 2):
            rr = r - dr
            if rr >= 0 and self.grid[rr][c] == v:
                count += 1
            else:
                break
        return count >= 3

    def print(self):
        header = "   " + " ".join(f"{c+1:2}" for c in range(self.cols))
        print(header)
        for r in range(self.rows):
            rowstr = f"{r+1:2} " + " ".join(self.grid[r][c] if self.grid[r][c] else '.' for c in range(self.cols))
            print(rowstr)
        print(f"Score: {self.score}")

    def in_bounds(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols
    
    def on_edges(self, r, c):
        return r == 0 or r == self.rows - 1 or c == 0 or c == self.cols - 1

    def are_adjacent(self, a, b):
        (r1, c1), (r2, c2) = a, b
        return abs(r1 - r2) + abs(c1 - c2) == 1

    def swap(self, a, b):
        (r1, c1), (r2, c2) = a, b
        self.grid[r1][c1], self.grid[r2][c2] = self.grid[r2][c2], self.grid[r1][c1]

    def find_matches(self):
        to_clear = set()
        # horizontal runs
        for r in range(self.rows):
            c = 0
            while c < self.cols:
                start = c
                v = self.grid[r][c]
                if v is None:
                    c += 1
                    continue
                c += 1
                while c < self.cols and self.grid[r][c] == v:
                    c += 1
                length = c - start
                if length >= 3:
                    for cc in range(start, c):
                        to_clear.add((r, cc))
        # vertical runs
        for c in range(self.cols):
            r = 0
            while r < self.rows:
                start = r
                v = self.grid[r][c]
                if v is None:
                    r += 1
                    continue
                r += 1
                while r < self.rows and self.grid[r][c] == v:
                    r += 1
                length = r - start
                if length >= 3:
                    for rr in range(start, r):
                        to_clear.add((rr, c))
        return to_clear

    def remove_matches(self, coords):
        if not coords:
            return 0
        # score: base 10 per gem, + bonus for longer combos
        n = len(coords)
        self.score += n * 10
        for (r, c) in coords:
            self.grid[r][c] = None
        return n

    def apply_gravity_and_refill(self):
        for c in range(self.cols):
            write_row = self.rows - 1
            for r in range(self.rows - 1, -1, -1):
                if self.grid[r][c] is not None:
                    self.grid[write_row][c] = self.grid[r][c]
                    write_row -= 1
            # fill remaining
            for r in range(write_row, -1, -1):
                self.grid[r][c] = self.random_gem()

    def resolve(self):
        # helper to flash matches on the screen before they are cleared
        flash_delay = 300  # milliseconds

        def _flash_matches(matches):
            if not matches:
                return
            # draw current board
            for r in range(self.rows):
                for c in range(self.cols):
                    gem = self.grid[r][c]
                    color = COLORS[gem] if gem else (255, 255, 255)
                    pygame.draw.rect(self.screen, color, (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, (0, 0, 0), (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
            # overlay highlights for matched cells
            for (r, c) in matches:
                pygame.draw.rect(self.screen, (255, 255, 255), (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
            pygame.display.flip()
            pygame.event.pump()
            pygame.time.wait(flash_delay)
        total_cleared = 0
        cascade = 0
        while True:
            matches = self.find_matches()
            _flash_matches(matches)
            if not matches:
                break
            cleared = self.remove_matches(matches)
            total_cleared += cleared
            cascade += 1
            self.apply_gravity_and_refill()
        return total_cleared, cascade


def parse_input(s):
    parts = s.strip().split()
    if len(parts) != 4:
        return None
    try:
        vals = [int(x) - 1 for x in parts]
    except ValueError:
        return None
    a = (vals[0], vals[1])
    b = (vals[2], vals[3])
    return a, b

"""
TODO:
add a win condition (score threshold or limited moves)
make a row appear at bottom and push up
"""
def main():
    print("Match-3 (terminal). Swap adjacent gems to form 3+ runs.")
    board = Board(rows=8, cols=8, gem_types=6)
    moves = 0
    # Initialize Pygame window
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    
                    pos = pygame.mouse.get_pos()
                    col = pos[0] // CELL_SIZE
                    row = pos[1] // CELL_SIZE
                    if board.selected is None:
                        board.selected = (row, col)
                    else:
                        if board.on_edges(row, col) or board.are_adjacent(board.selected, (row, col)):
                            board.swap(board.selected, (row, col))
                            matches = board.find_matches()
                            if matches:
                                cleared, cascades = board.resolve()
                                print(f"Cleared {cleared} gems with {cascades} cascade(s). Moves: {moves}")

                        board.selected = None

        board.screen.fill((255, 255, 255))  # Clear screen
        for r in range(board.rows):
            for c in range(board.cols):
                gem = board.grid[r][c]
                color = COLORS[gem] if gem else (255, 255, 255)  # White for empty
                pygame.draw.rect(board.screen, color, (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(board.screen, (0, 0, 0), (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)  # Grid lines
                if board.selected == (r, c):
                    pygame.draw.rect(board.screen, (255, 225, 225), (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)  # Highlight selected gem
        
        pygame.display.flip()
        clock.tick(30)  # Limit to 30 frames per second

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Bye.")
        sys.exit(0)