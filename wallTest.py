import pygame
import ctypes
import math
from datetime import datetime

now = datetime.now()

hour = now.hour
minute = now.minute
second = now.second

# Get screen size
user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)

pygame.init()

# Create borderless window (fullscreen)
screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)

# Set window title
pygame.display.set_caption("Wallpaper Prototype")

# Fill with color (test background)
background_color = (120, 150, 180)

scale = 8

Bframes = []
for i in range(4):
    img = pygame.image.load(f"Bee/bee_{i}.png")
    img = pygame.transform.scale(img, (5 * scale, 5 * scale))
    Bframes.append(img)

Bframes_flipped = []
for img in Bframes:
    flipped = pygame.transform.flip(img, True, False)
    Bframes_flipped.append(flipped)

Fframes = []
for i in range(24):
    img = pygame.image.load(f"FlowerClockv2/FlowerV2_{i:02}.png")
    img = pygame.transform.scale(img, (32 * scale, 32 * scale))
    Fframes.append(img)


Bframe_index = 0
Blast_update = 0
Bframe_delay = 250  # milliseconds (4 FPS)

running = True

while running:
    current_time = pygame.time.get_ticks()

    now = datetime.now()

    hour = now.hour
    minute = now.minute
    second = now.second

    flower_index = (hour - 1) % 24

    if current_time - Blast_update >= Bframe_delay:
        Bframe_index = (Bframe_index + 1) % len(Bframes)
        Blast_update = current_time
    
    
    screen_rect = screen.get_rect()
    center_x, center_y = screen_rect.center

    Bradius = 150

    flower_rect = Fframes[flower_index].get_rect(center=screen_rect.center)
    
    Bangle = (minute / 60) * 2 * math.pi
    Bangle -= math.pi / 2

    Bx = center_x + math.cos(Bangle) * Bradius
    By = center_y + math.sin(Bangle) * Bradius
    
    if Bx < center_x:
        Bcurrent_frame = Bframes[Bframe_index]          # left side → face right
    else:
        Bcurrent_frame = Bframes_flipped[Bframe_index]  # right side → face left

    screen.fill(background_color)
    screen.blit(Bcurrent_frame, (Bx, By))
    screen.blit(Fframes[flower_index], flower_rect)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    
    pygame.display.update()

pygame.quit()