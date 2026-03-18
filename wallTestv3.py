import pygame
import ctypes
import math
from datetime import datetime
import keyboard

def quit_app():
    global running
    running = False
keyboard.add_hotkey("esc", quit_app)

now = datetime.now()

hour = now.hour
minute = now.minute
second = now.second

# Get screen size
user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)

pygame.init()

import win32gui
import win32con
import win32api

def set_as_wallpaper(hwnd):
    progman = win32gui.FindWindow("Progman", None)

    # Tell Windows to create WorkerW behind icons
    win32gui.SendMessageTimeout(progman, 0x052C, 0, 0, win32con.SMTO_NORMAL, 1000)

    def enum_windows_callback(hwnd, windows):
        if win32gui.FindWindowEx(hwnd, None, "SHELLDLL_DefView", None):
            workerw = win32gui.FindWindowEx(None, hwnd, "WorkerW", None)
            windows.append(workerw)
        return True

    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)

    if windows:
        workerw = windows[0]
        win32gui.SetParent(hwnd, workerw)


screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
hwnd = pygame.display.get_wm_info()['window']
set_as_wallpaper(hwnd)
win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, win32con.WS_VISIBLE)



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

fake_time_seconds = 0
Bframe_index = 0
Blast_update = 0
Bframe_delay = 250  # milliseconds (4 FPS)

running = True
USE_REAL_TIME = False
while running:
    current_time = pygame.time.get_ticks()

    if USE_REAL_TIME:
        now = datetime.now()
    else:
        total_seconds = fake_time_seconds % (24 * 3600)

        hour = total_seconds // 3600
        minute = (total_seconds % 3600) // 60
        second = total_seconds % 60

        class FakeTime:
            def __init__(self, h, m, s):
                self.hour = h
                self.minute = m
                self.second = s
                self.microsecond = 0

        now = FakeTime(hour, minute, second)

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
    bee_rect = Bcurrent_frame.get_rect(center=(Bx, By))
    screen.blit(Bcurrent_frame, bee_rect)
    screen.blit(Fframes[flower_index], flower_rect)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_RIGHT:
                fake_time_seconds += 60  # +1 minute
            if event.key == pygame.K_LEFT:
                fake_time_seconds -= 60  # -1 minute

    
    pygame.display.update()

pygame.quit()
