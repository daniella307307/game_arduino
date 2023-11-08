import pygame
import sys
import random
import serial

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 500, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Car Driving Game')

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Load car image and resize it
car = pygame.image.load('car.png')
car = pygame.transform.scale(car, (90, 150))
car_rect = car.get_rect(center=(WIDTH // 2, HEIGHT - 100))

# Load obstacle image and resize it
obstacle = pygame.image.load('obstacle1.png')
obstacle = pygame.transform.scale(obstacle, (100, 80))

# Load road image
road = pygame.image.load('road.png')
road = pygame.transform.scale(road, (WIDTH, HEIGHT))
road_y = 0

# Load sounds
collision_sound = pygame.mixer.Sound('collision_sound.wav')
collect_sound = pygame.mixer.Sound('collect_sound.wav')

# Initialize obstacle variables
obstacle_speed = 20
obstacles = []
obstacles_avoided = 0  # Keep track of obstacles avoided

passed_obstacles = 0  # Count of obstacles passed
finishing_line_y = -30  # Initial position of the finishing line

score = 0
font = pygame.font.Font(None, 36)

paused = False  # Variable to control pause state
pause_text = font.render('PAUSED', True, RED)  # Pause text

def display_score(score):
    score_text = font.render(f'Score: {score}', True, BLACK)
    screen.blit(score_text, (10, 10))

def spawn_obstacle():
    x = random.randint(50, WIDTH - 50)
    y = -50
    return obstacle.get_rect(topleft=(x, y))

def display_message(text, x, y, color):
    message = font.render(text, True, color)
    screen.blit(message, (x, y))

try:
    # Initialize Serial Communication
    ser = serial.Serial('COM20', 9600)

    # Game loop
    running = True
    game_over = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Check for pause toggle (P key)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                paused = not paused

        if not paused:
            try:
                # Read joystick values from Arduino
                joystick_data = ser.readline().decode().strip().split(',')
                if len(joystick_data) == 2:
                    joyX = int(joystick_data[0])
                    joyY = int(joystick_data[1])

                    if not game_over:
                        # Update car's position based on joystick values
                        car_rect.move_ip((joyX - 512) / 20, (joyY - 512) / 20)

                        # Ensure car stays within window bounds
                        car_rect.left = max(0, car_rect.left)
                        car_rect.right = min(WIDTH, car_rect.right)
                        car_rect.top = max(0, car_rect.top)
                        car_rect.bottom = min(HEIGHT, car_rect.bottom)

                        # Spawn new obstacles
                        if pygame.time.get_ticks() % 60 == 0:
                            obstacles.append(spawn_obstacle())

                        # Move and remove obstacles
                        for obs in obstacles[:]:
                            obs.move_ip(0, obstacle_speed)
                            if obs.top > HEIGHT:
                                obstacles.remove(obs)
                                score += 1
                                passed_obstacles += 1  # Increment the number of obstacles passed

                                if passed_obstacles == 10:
                                    # Move the finishing line down and display a winning message
                                    finishing_line_y += 30
                                    passed_obstacles = 0
                                    game_over = True  # Game is won

                        # Check for collisions with obstacles
                        for obs in obstacles[:]:
                            if car_rect.colliderect(obs):
                                game_over = True
                                collision_sound.play()

                    # Draw everything
                    road_y = (road_y + 5) % HEIGHT
                    screen.blit(road, (0, road_y))
                    screen.blit(road, (0, road_y - HEIGHT))
                    screen.blit(car, car_rect)

                    for obs in obstacles:
                        screen.blit(obstacle, obs)

                    # Draw the finishing line
                    pygame.draw.rect(screen, BLACK, (0, finishing_line_y, WIDTH, 5))

                    display_score(score)

                    if game_over:
                        if score >= 10:
                            collect_sound.play()
                            display_message("You Won! Press 'R' to Restart", 90, 100, RED)
                        else:
                            display_message("Game Over! Press 'R' to Restart", 90, 100, RED)

            except ValueError as e:
                print(f"Error: {e}. Invalid data received from Arduino.")

        else:
            # Display "PAUSED" text when the game is paused
            screen.blit(pause_text, (WIDTH // 2 - 40, HEIGHT // 2 - 20))

        # Restart the game if 'R' is pressed
        keys = pygame.key.get_pressed()
        if (game_over or score >= 10) and keys[pygame.K_r]:
            game_over = False
            score = 0
            obstacles.clear()
            obstacle_speed = 20  # Reset the obstacle speed
            passed_obstacles = 0
            finishing_line_y = -30  # Reset the finishing line position

        pygame.display.flip()

except serial.SerialException as se:
    print(f"Error: {se}. Unable to establish a connection to the Arduino.")
except Exception as e:
    print(f"Error: {e}. An unexpected error occurred.")

# Clean up
pygame.quit()
sys.exit()


