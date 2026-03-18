import pygame
import ctypes
import math
from datetime import datetime

#make sure to remove this section for development.
import keyboard

def quit_app():
    global running
    running = False
keyboard.add_hotkey("esc", quit_app)
#section end

Fallback = True

#I am not sure why I have two of these.
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
    global Fallback
    progman = win32gui.FindWindow("Progman", None)

    # Try multiple times (this is the key fix)
    for _ in range(5):
        win32gui.SendMessageTimeout(
            progman,
            0x052C,
            0,
            0,
            win32con.SMTO_NORMAL,
            1000
        )

    workerw = None

    def enum_windows_callback(top_hwnd, _):
        nonlocal workerw

        shell = win32gui.FindWindowEx(top_hwnd, None, "SHELLDLL_DefView", None)
        if shell:
            # Try to get WorkerW
            workerw_candidate = win32gui.FindWindowEx(None, top_hwnd, "WorkerW", None)
            if workerw_candidate:
                workerw = workerw_candidate

    win32gui.EnumWindows(enum_windows_callback, None)

    if workerw:
        print("WorkerW found:", workerw)
        win32gui.SetParent(hwnd, workerw)
        Fallback = False
    else:
        print("WorkerW STILL not found")
        Fallback = True
        



screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
hwnd = pygame.display.get_wm_info()['window']
set_as_wallpaper(hwnd)

# Set window title
pygame.display.set_caption("Wallpaper Prototype")

# Fill with color (test background)
if Fallback:
    background_color = (255, 0, 255)
    styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(
        hwnd,
        win32con.GWL_EXSTYLE,
        styles | win32con.WS_EX_LAYERED
    )

    win32gui.SetLayeredWindowAttributes(
        hwnd,
        win32api.RGB(*background_color),
        0,
        win32con.LWA_COLORKEY
)

else:
    background_color = (120, 150, 180)
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, win32con.WS_VISIBLE)


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
USE_REAL_TIME = True
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
