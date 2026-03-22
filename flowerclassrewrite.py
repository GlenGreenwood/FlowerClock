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




exit_socket = None

scale = 8

class Bee:
    def __init__(self, scale, radius=150):
        self.scale = scale
        self.radius = radius

        self.frames = []

        self.frames_flipped = []

        self.current_frame = None

        self.last_update = 0
        self.frame_index = 0
        self.frame_delay = 250
        self.x = 0
        self.y = 0
bee = Bee(scale)



class Flower:
    def __init__(self):
        self.frames = []
        self.index = 0
        
flower = Flower()
    



fake_time_seconds = 0


USE_REAL_TIME = True
clock = pygame.time.Clock()




running = True
pygame.init()

for i in range(4):
    img = pygame.image.load(os.path.join(BASE_PATH, "Bee", f"bee_{i}.png"))
    img = pygame.transform.scale(img, (5 * scale, 5 * scale))
    bee.frames.append(img)
for img in bee.frames:
    flipped = pygame.transform.flip(img, True, False)
    bee.frames_flipped.append(flipped)
for i in range(24):
    img = pygame.image.load(os.path.join(BASE_PATH, "FlowerClockv2", f"FlowerV2_{i:02}.png"))
    img = pygame.transform.scale(img, (32 * scale, 32 * scale))
    flower.frames.append(img)




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

pygame.display.set_caption("Flower Clock")

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

def get_time_tint(hour, minute):
    t = (hour + minute / 60) / 24
    brightness = (math.sin(t * 2 * math.pi - math.pi/2) + 1) / 2
    darkness = 1 - brightness
    alpha = int(120 * darkness)
    return (10, 20, 60, alpha)





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






#classy flower
    flower.index = (hour - 1) % 24
#classy bee
    if current_time - bee.last_update >= bee.frame_delay:
        bee.frame_index = (bee.frame_index + 1) % len(bee.frames)
        bee.last_update = current_time

    screen_rect = screen.get_rect()
    center_x, center_y = screen_rect.center
#classy flower?
    flower_rect = flower.frames[flower.index].get_rect(center=screen_rect.center)
#classy bee
    bee.radius = 150
    bee.angle = (minute / 60) * 2 * math.pi
    bee.angle -= math.pi / 2
    bee.x = center_x + math.cos(bee.angle) * bee.radius
    bee.y = center_y + math.sin(bee.angle) * bee.radius
    if bee.x < center_x:
        bee.current_frame = bee.frames[bee.frame_index]
    else:
        bee.current_frame = bee.frames_flipped[bee.frame_index]

    if Fallback:
        tint = get_time_tint(hour, minute)
        overlay.fill(tint)
        screen.blit(overlay, (0, 0))

    screen.fill(background_color)
#classy bee
    bee_rect = bee.current_frame.get_rect(center=(bee.x, bee.y))
    screen.blit(bee.current_frame, bee_rect)
#classy flower
    screen.blit(flower.frames[flower.index], flower_rect)


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


pygame.quit()
