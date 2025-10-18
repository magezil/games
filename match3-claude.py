import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
GRID_WIDTH = 8
GRID_HEIGHT = 8
GEM_SIZE = 64
WINDOW_WIDTH = GRID_WIDTH * GEM_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * GEM_SIZE

# Colors
COLORS = {
    'red': (255, 0, 0),
    'blue': (0, 0, 255),
    'green': (0, 255, 0),
    'yellow': (255, 255, 0),
    'purple': (128, 0, 128)
}
COLOR_NAMES = list(COLORS.keys())

class Gem:
    def __init__(self, x, y, color_name):
        self.grid_x = x
        self.grid_y = y
        self.color_name = color_name
        self.color = COLORS[color_name]
        # Actual pixel position
        self.x = x * GEM_SIZE
        self.y = y * GEM_SIZE
        # Target position for animation
        self.target_x = self.x
        self.target_y = self.y
        self.selected = False
    
    def draw(self, screen):
        # Simple rectangle representation
        padding = 2
        rect = pygame.Rect(self.x + padding, self.y + padding, 
                          GEM_SIZE - padding * 2, GEM_SIZE - padding * 2)
        
        # Highlight if selected
        color = self.color
        if self.selected:
            color = tuple(min(255, c + 50) for c in self.color)
        
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)  # Border
    
    def update(self):
        # Smooth animation towards target position
        speed = 10
        if self.x < self.target_x:
            self.x = min(self.x + speed, self.target_x)
        elif self.x > self.target_x:
            self.x = max(self.x - speed, self.target_x)
        
        if self.y < self.target_y:
            self.y = min(self.y + speed, self.target_y)
        elif self.y > self.target_y:
            self.y = max(self.y - speed, self.target_y)
    
    def is_animating(self):
        return self.x != self.target_x or self.y != self.target_y
    
    def contains_point(self, pos):
        return (self.x <= pos[0] < self.x + GEM_SIZE and 
                self.y <= pos[1] < self.y + GEM_SIZE)

class Match3Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Match-3 Game")
        self.clock = pygame.time.Clock()
        self.grid = []
        self.selected_gem = None
        self.create_grid()
    
    def create_grid(self):
        for y in range(GRID_HEIGHT):
            row = []
            for x in range(GRID_WIDTH):
                color_name = random.choice(COLOR_NAMES)
                gem = Gem(x, y, color_name)
                row.append(gem)
            self.grid.append(row)
    
    def are_adjacent(self, gem1, gem2):
        dx = abs(gem1.grid_x - gem2.grid_x)
        dy = abs(gem1.grid_y - gem2.grid_y)
        return (dx == 1 and dy == 0) or (dx == 0 and dy == 1)
    
    def swap_gems(self, gem1, gem2):
        # Swap grid positions
        x1, y1 = gem1.grid_x, gem1.grid_y
        x2, y2 = gem2.grid_x, gem2.grid_y
        
        self.grid[y1][x1] = gem2
        self.grid[y2][x2] = gem1
        
        # Update grid coordinates
        gem1.grid_x, gem1.grid_y = x2, y2
        gem2.grid_x, gem2.grid_y = x1, y1
        
        # Set target positions for animation
        gem1.target_x = x2 * GEM_SIZE
        gem1.target_y = y2 * GEM_SIZE
        gem2.target_x = x1 * GEM_SIZE
        gem2.target_y = y1 * GEM_SIZE
    
    def is_animating(self):
        for row in self.grid:
            for gem in row:
                if gem.is_animating():
                    return True
        return False
    
    def find_matches(self):
        matches = []
        
        # Check horizontal matches
        for y in range(GRID_HEIGHT):
            match_count = 1
            for x in range(1, GRID_WIDTH):
                if self.grid[y][x].color_name == self.grid[y][x-1].color_name:
                    match_count += 1
                else:
                    if match_count >= 3:
                        for i in range(match_count):
                            matches.append(self.grid[y][x-1-i])
                    match_count = 1
            if match_count >= 3:
                for i in range(match_count):
                    matches.append(self.grid[y][GRID_WIDTH-1-i])
        
        # Check vertical matches
        for x in range(GRID_WIDTH):
            match_count = 1
            for y in range(1, GRID_HEIGHT):
                if self.grid[y][x].color_name == self.grid[y-1][x].color_name:
                    match_count += 1
                else:
                    if match_count >= 3:
                        for i in range(match_count):
                            matches.append(self.grid[y-1-i][x])
                    match_count = 1
            if match_count >= 3:
                for i in range(match_count):
                    matches.append(self.grid[GRID_HEIGHT-1-i][x])
        
        return matches
    
    def handle_click(self, pos):
        if self.is_animating():
            return
        
        # Find clicked gem
        clicked_gem = None
        for row in self.grid:
            for gem in row:
                if gem.contains_point(pos):
                    clicked_gem = gem
                    break
            if clicked_gem:
                break
        
        if not clicked_gem:
            return
        
        if self.selected_gem is None:
            # First selection
            self.selected_gem = clicked_gem
            clicked_gem.selected = True
        else:
            if clicked_gem == self.selected_gem:
                # Deselect
                self.selected_gem.selected = False
                self.selected_gem = None
            elif self.are_adjacent(self.selected_gem, clicked_gem):
                # Swap gems - ALWAYS allow (your requirement)
                self.swap_gems(self.selected_gem, clicked_gem)
                self.selected_gem.selected = False
                self.selected_gem = None
            else:
                # Select different gem
                self.selected_gem.selected = False
                self.selected_gem = clicked_gem
                clicked_gem.selected = True
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
            
            # Update all gems (for animation)
            for row in self.grid:
                for gem in row:
                    gem.update()
            
            # Check for matches after animation completes
            if not self.is_animating() and self.selected_gem is None:
                matches = self.find_matches()
                if matches:
                    print(f"Matches found: {len(matches)}")
                    # Here you'd handle removing matches, scoring, etc.
            
            # Draw
            self.screen.fill((30, 30, 30))
            for row in self.grid:
                for gem in row:
                    gem.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Match3Game()
    game.run()