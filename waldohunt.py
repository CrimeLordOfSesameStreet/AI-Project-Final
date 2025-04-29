import pygame
import random
import time
import os
import sys
import torch
from ultralytics import YOLO

#Made by Isaac Barrera, for CSC 3400 AI Project Final under Dr. Joshua Locklair

waiting_for_mouse_release = False
decrease_clicked = False
increase_clicked = False

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(script_dir)

# Calls the Wheres Waldo images
image_folder = "waldo_images"
pygame.init()
pygame.mixer.init()

# Sets the window size, otherwize it is zoomed in way too far
screen_width = 1280
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("WaldoHunt")


font = pygame.font.SysFont(None, 90)
small_font = pygame.font.SysFont(None, 40)
timer_font = pygame.font.SysFont(None, 80)

# Loads the trained YOLOv11 model
model_path = "waldohunter.pt"
model = YOLO(model_path)

#default seconds to find Waldo
reveal_delay = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (100, 100, 100)
TIMER_COLOR = (255, 0, 0)

# Music, credits in README.txt file in directory I DID NOT MAKE THESE!
background_music_path = "maintheme.mp3"
gameover_music_path = "gameover.mp3"

# Player score and "level"
player_score = 0

# title screen image
title_background_path = "machineishere.jpg"
if not os.path.exists(title_background_path):
    print(f"Missing {title_background_path} file!")
    sys.exit()
title_background = pygame.image.load(title_background_path)
title_background = pygame.transform.scale(title_background, (screen_width, screen_height))

# using pygame music functions to play music
def play_background_music():
    pygame.mixer.music.load(background_music_path)
    pygame.mixer.music.play(-1)
def play_gameover_music():
    pygame.mixer.music.load(gameover_music_path)
    pygame.mixer.music.play()
def stop_music():
    pygame.mixer.music.stop()

def quit_game():
    pygame.quit()
    sys.exit()

def load_image(image_path):
    return pygame.image.load(image_path)

def detect_waldo(image_path):
    results = model(image_path)
    predictions = results[0].boxes.xyxy
    if predictions is None or len(predictions) == 0:
        return None
    confidences = results[0].boxes.conf
    best_idx = confidences.argmax()

    box = predictions[best_idx].tolist()
    return box

def clamp(val, min_val, max_val):
    return max(min_val, min(val, max_val))

def draw_text(text, font, color, surface, x, y):
    if not isinstance(text, str):
        text = ""
    textobj = font.render(text, True, color)
    rect = textobj.get_rect()
    rect.center = (x, y)
    surface.blit(textobj, rect)

def button(text, x, y, width, height, action=None):
    global waiting_for_mouse_release
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    clicked = False
    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(screen, GRAY, (x, y, width, height))
        if click[0] == 1:
            clicked = True
    else:
        pygame.draw.rect(screen, WHITE, (x, y, width, height))

    draw_text(text, small_font, BLACK, screen, x + width // 2, y + height // 2)

    if clicked and not waiting_for_mouse_release and action:
        return action
    return None

def title_screen():
    global waiting_for_mouse_release
    waiting_for_mouse_release = True

    while True:
        screen.blit(title_background, (0, 0))

        draw_text('WaldoHunt.EXE', font, RED, screen, screen_width // 2, screen_height // 5)
        draw_text('Created by Isaac Barrera', small_font, WHITE, screen, screen_width // 2, screen_height // 5 + 80)
        draw_text('Double Click to Start!', small_font, WHITE, screen, screen_width // 2, screen_height // 5 + 120)


        start_action = button("Start Game", screen_width // 2 - 100, screen_height // 2 + 100, 200, 60, 'start')
        settings_action = button("Settings", screen_width // 2 - 100, screen_height // 2 + 200, 200, 60, 'settings')
        controls_action = button("Controls", screen_width // 2 - 100, screen_height // 2 + 300, 200, 60, 'controls')

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONUP:
                waiting_for_mouse_release = False

        if not waiting_for_mouse_release:
            if start_action == 'start':
                return 'start'
            if settings_action == 'settings':
                return 'settings'
            if controls_action == 'controls':
                return 'controls'

        pygame.display.update()

def settings_screen():
    global reveal_delay, waiting_for_mouse_release
    waiting_for_mouse_release = True

    input_box = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 50, 200, 50)
    user_text = ''
    active = False  # Is the input box active?

    while True:
        screen.fill(BLACK)
        draw_text('Settings', font, WHITE, screen, screen_width // 2, screen_height // 4)
        draw_text(f'Time Before AI HUNT: {reveal_delay} seconds', small_font, WHITE, screen, screen_width // 2, screen_height // 2 - 50)
        draw_text('Type new time and press Enter:', small_font, WHITE, screen, screen_width // 2, screen_height // 2)

        # Draw input box
        color = GRAY if active else WHITE
        pygame.draw.rect(screen, color, input_box, 2)

        text_surface = small_font.render(user_text, True, WHITE)
        screen.blit(text_surface, (input_box.x + 5, input_box.y + 10))
        input_box.w = max(200, text_surface.get_width() + 10)

        back_action = button("Back", screen_width // 2 - 100, screen_height // 2 + 150, 200, 60, 'back')

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False
                waiting_for_mouse_release = False
            if event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN:
                    try:
                        typed_value = int(user_text)
                        if 1 <= typed_value <= 600:
                            reveal_delay = typed_value
                        else:
                            print("Value out of allowed range (1-600 seconds).")
                    except ValueError:
                        print("Invalid input. Please type a number.")
                    user_text = ''
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    if event.unicode.isdigit():
                        user_text += event.unicode

        if not waiting_for_mouse_release:
            if back_action == 'back':
                return 'title'

        pygame.display.update()



def controls_screen():
    global waiting_for_mouse_release
    waiting_for_mouse_release = True

    while True:
        screen.fill(BLACK)
        draw_text('How to Play', font, WHITE, screen, screen_width // 2, screen_height // 4)
        draw_text('Left Click + Drag to move image panel', small_font, WHITE, screen, screen_width // 2, screen_height // 2 - 50)
        draw_text('Mouse Wheel or +/- to zoom in/out', small_font, WHITE, screen, screen_width // 2, screen_height // 2)
        draw_text('Press "Found Waldo" button when you find him (DO NOT CHEAT ITS LAME!)', small_font, WHITE, screen, screen_width // 2, screen_height // 2 + 50)
        draw_text('GOAL: FIND WALDO BEFORE THE MACHINE (AI) FINDS HIM!', small_font, WHITE, screen, screen_width // 2, screen_height // 2 + 100)
        back_action = button("Back", screen_width // 2 - 100, screen_height // 2 + 150, 200, 60, 'back')

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONUP:
                waiting_for_mouse_release = False

        if not waiting_for_mouse_release:
            if back_action == 'back':
                return 'title'
        pygame.display.update()

def decrease_time():
    global reveal_delay
    reveal_delay = max(1, reveal_delay - 1)

def increase_time():
    global reveal_delay
    reveal_delay = min(180, reveal_delay + 1)

def game_loop():
    global found_waldo, player_score, waiting_for_mouse_release, gameover_music_playing
    found_waldo = False
    machine_found_waldo = False

    running = True
    clock = pygame.time.Clock()

    image_files = os.listdir(image_folder)
    image_filename = random.choice(image_files)
    image_path = os.path.join(image_folder, image_filename)
    original_image = load_image(image_path)

    img_width, img_height = original_image.get_width(), original_image.get_height()

    zoom_scale = 0.2
    offset_x = 0
    offset_y = 0

    start_time = time.time()
    waldo_box = None
    detection_done = False

    dragging = False

    while running:
        screen.fill(BLACK)
#Prevents issues with gameover soundtrack
        if gameover_music_path and not pygame.mixer.music.get_busy():
            play_background_music()
            gameover_music_playing = False

        scaled_width = int(img_width * zoom_scale)
        scaled_height = int(img_height * zoom_scale)
        image = pygame.transform.smoothscale(original_image, (scaled_width, scaled_height))

        img_rect = image.get_rect()
        img_rect.center = (screen_width // 2 + offset_x, screen_height // 2 + offset_y)
        screen.blit(image, img_rect)

        elapsed_time = time.time() - start_time
        time_left = max(0, reveal_delay - elapsed_time)

        timer_text = f"Time Left: {int(time_left)}"
        draw_text(timer_text, timer_font, TIMER_COLOR, screen, screen_width // 2, 50)

        draw_text(f"Level: {player_score}", small_font, RED, screen, 100, 50)

        if elapsed_time > reveal_delay and not detection_done and not found_waldo:
            waldo_box = detect_waldo(image_path)
            detection_done = True
            machine_found_waldo = True
            player_score = 0
            stop_music()
            play_gameover_music()
            gameover_music_playing = True

        if waldo_box is not None:
            xmin, ymin, xmax, ymax = waldo_box
            box_width = xmax - xmin
            box_height = ymax - ymin

            xmin_scaled = xmin * zoom_scale
            ymin_scaled = ymin * zoom_scale
            box_width_scaled = box_width * zoom_scale
            box_height_scaled = box_height * zoom_scale

            rect_x = img_rect.left + xmin_scaled
            rect_y = img_rect.top + ymin_scaled

            pygame.draw.rect(screen, RED, (rect_x, rect_y, box_width_scaled, box_height_scaled), 4)

        if found_waldo:
            draw_text("You found Waldo!", font, RED, screen, screen_width // 2, screen_height // 2)

            if button("Back to Title", screen_width // 2 - 200, screen_height // 2 + 100, 180, 60, 'back') == 'back':
                play_background_music()
                gameover_music_playing = False
                return
            if button("Next Level", screen_width // 2 + 20, screen_height // 2 + 100, 180, 60, 'next') == 'next':
                player_score += 1
                return 'next'

        elif machine_found_waldo:
            draw_text("MACHINE FOUND WALDO: GAME OVER!", font, RED, screen, screen_width // 2, screen_height // 2)

            if button("Back to Title", screen_width // 2 - 200, screen_height // 2 + 100, 180, 60, 'back') == 'back':
                play_background_music()
                gameover_music_playing = False
                return
            if button("Next Level", screen_width // 2 + 20, screen_height // 2 + 100, 180, 60, 'next') == 'next':
                player_score += 1
                return 'next'

        else:
            if button("Found Waldo", screen_width // 2 - 100, screen_height // 2 + 250, 200, 60, 'found') == 'found':
                found_waldo_function()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging = True
                    drag_start_pos = event.pos

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False

            if event.type == pygame.MOUSEMOTION:
                if dragging:
                    dx, dy = event.rel
                    offset_x += dx
                    offset_y += dy

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    zoom_scale = min(5.0, zoom_scale + 0.05)
                if event.key == pygame.K_MINUS:
                    zoom_scale = max(0.05, zoom_scale - 0.05)

        max_offset_x = max(0, (scaled_width - screen_width) // 2)
        max_offset_y = max(0, (scaled_height - screen_height) // 2)

        offset_x = clamp(offset_x, -max_offset_x, max_offset_x)
        offset_y = clamp(offset_y, -max_offset_y, max_offset_y)

        pygame.display.update()
        clock.tick(60)

def found_waldo_function():
    global found_waldo
    found_waldo = True

if __name__ == "__main__":
    try:
        play_background_music()
        current_screen = 'title'
        running = True
        while running:
            if current_screen == 'title':
                current_screen = title_screen()
            elif current_screen == 'settings':
                current_screen = settings_screen()
            elif current_screen == 'controls':
                current_screen = controls_screen()
            elif current_screen == 'start':
                result = game_loop()
                if result == 'next':
                    current_screen = 'start'
                else:
                    current_screen = 'title'
            else:
                running = False

        quit_game()

    except Exception as e:
        with open("error_log.txt", "w") as f:
            f.write(str(e))
