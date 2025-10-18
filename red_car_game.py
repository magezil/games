import pygame
import sys

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Red Car Game")

# Colors
RED = (220, 20, 60)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)

# Car settings
car_width, car_height = 60, 30 // 2
car_x, car_y = WIDTH // 2 - car_width, HEIGHT - car_height - 20

car_speed = 5
clock = pygame.time.Clock()

# Main loop
running = True
while running:
    screen.fill(GRAY)
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Key handling
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and car_x > 0:
        car_x -= car_speed
    if keys[pygame.K_RIGHT] and car_x < WIDTH - car_width:
        car_x += car_speed

    # Draw car (simple rectangle)
    pygame.draw.rect(screen, RED, (car_x, car_y, car_width, car_height))
    # Draw wheels
    pygame.draw.circle(screen, (0, 0, 0), (car_x + 10, car_y + car_height), 8)
    pygame.draw.circle(screen, (0, 0, 0), (car_x + car_width - 10, car_y + car_height), 8)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
