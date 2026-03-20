import pygame
import ctypes
import math
from datetime import datetime
import win32gui
import win32con
import win32api
import socket
import threading
import time
import atexit
import keyboard
import os
import sys

running = True
def quit_app():
    global running
    running = False
keyboard.add_hotkey("esc", quit_app)

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)

BASE_PATH = get_base_path()

Fallback = True

now = datetime.now()

hour = now.hour
minute = now.minute
second = now.second

user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)

pygame.init()

def set_as_wallpaper(hwnd):
    global Fallback
    progman = win32gui.FindWindow("Progman", None)
    for _ in range(5):
        win32gui.SendMessageTimeout(
            progman,
            0x052C,
            0,
            0,
            win32con.SMTO_NORMAL,
            1000
        )
    time.sleep(0.1)
    workerw = None

    def enum_windows_callback(top_hwnd, _):
        nonlocal workerw
        shell = win32gui.FindWindowEx(top_hwnd, None, "SHELLDLL_DefView", None)
        if shell:
            workerw_candidate = win32gui.FindWindowEx(None, top_hwnd, "WorkerW", None)
            if workerw_candidate:
                workerw = workerw_candidate

    win32gui.EnumWindows(enum_windows_callback, None)

    if workerw:
        win32gui.SetParent(hwnd, workerw)
    else:
        Fallback = True

exit_socket = None

def listen_for_exit():
    global running, exit_socket
    exit_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    exit_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    exit_socket.bind(("localhost", 65432))
    exit_socket.listen(1)
    exit_socket.settimeout(1.0)

    while running:
        try:
            conn, _ = exit_socket.accept()
            with conn:
                data = conn.recv(1024)
                if data == b"exit":
                    running = False
        except socket.timeout:
            continue
        except Exception:
            break

    try:
        exit_socket.close()
    except Exception:
        pass

threading.Thread(target=listen_for_exit, daemon=True).start()

screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
hwnd = pygame.display.get_wm_info()['window']
win32gui.SetWindowPos(
    hwnd,
    win32con.HWND_BOTTOM,
    0, 0, 0, 0,
    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
)
set_as_wallpaper(hwnd)

pygame.display.set_caption("Wallpaper Prototype")

if Fallback:
    background_color = (255, 0, 255)
    styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(
        hwnd,
        win32con.GWL_EXSTYLE,
        styles | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOOLWINDOW
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

def get_time_tint(hour, minute):
    t = (hour + minute / 60) / 24
    brightness = (math.sin(t * 2 * math.pi - math.pi/2) + 1) / 2
    darkness = 1 - brightness
    alpha = int(120 * darkness)
    return (10, 20, 60, alpha)

scale = 8

Bframes = []
for i in range(4):
    img = pygame.image.load(os.path.join(BASE_PATH, "Bee", f"bee_{i}.png"))
    img = pygame.transform.scale(img, (5 * scale, 5 * scale))
    Bframes.append(img)

Bframes_flipped = []
for img in Bframes:
    flipped = pygame.transform.flip(img, True, False)
    Bframes_flipped.append(flipped)

Fframes = []
for i in range(24):
    img = pygame.image.load(os.path.join(BASE_PATH, "FlowerClockv2", f"FlowerV2_{i:02}.png"))
    img = pygame.transform.scale(img, (32 * scale, 32 * scale))
    Fframes.append(img)

fake_time_seconds = 0
Bframe_index = 0
Blast_update = 0
Bframe_delay = 250

USE_REAL_TIME = True
clock = pygame.time.Clock()

while running:
    current_time = pygame.time.get_ticks()
    clock.tick(60)
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

    if keyboard.is_pressed("right"):
        fake_time_seconds += 60

    if keyboard.is_pressed("left"):
        fake_time_seconds -= 60

    flower_index = (hour - 1) % 24

    if current_time - Blast_update >= Bframe_delay:
        Bframe_index = (Bframe_index + 1) % len(Bframes)
        Blast_update = current_time

    screen_rect = screen.get_rect()
    center_x, center_y = screen_rect.center

    flower_rect = Fframes[flower_index].get_rect(center=screen_rect.center)

    Bradius = 150
    Bangle = (minute / 60) * 2 * math.pi
    Bangle -= math.pi / 2

    Bx = center_x + math.cos(Bangle) * Bradius
    By = center_y + math.sin(Bangle) * Bradius

    if Bx < center_x:
        Bcurrent_frame = Bframes[Bframe_index]
    else:
        Bcurrent_frame = Bframes_flipped[Bframe_index]

    if Fallback:
        tint = get_time_tint(hour, minute)
        overlay.fill(tint)
        screen.blit(overlay, (0, 0))

    screen.fill(background_color)

    bee_rect = Bcurrent_frame.get_rect(center=(Bx, By))
    screen.blit(Bcurrent_frame, bee_rect)

    screen.blit(Fframes[flower_index], flower_rect)

    if not Fallback:
        tint = get_time_tint(hour, minute)
        overlay.fill(tint)
        screen.blit(overlay, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_RIGHT:
                fake_time_seconds += 60
            if event.key == pygame.K_LEFT:
                fake_time_seconds -= 60

    pygame.display.update()

try:
    if win32gui.IsWindow(hwnd):
        win32gui.SetParent(hwnd, 0)
except Exception:
    pass

time.sleep(0.05)

try:
    ctypes.windll.user32.RedrawWindow(
        0, None, None,
        0x0001 | 0x0004 | 0x0400
    )
except Exception:
    pass

try:
    progman = win32gui.FindWindow("Progman", None)
    ctypes.windll.user32.InvalidateRect(progman, None, True)
    win32gui.UpdateWindow(progman)
except Exception:
    pass

pygame.quit()
