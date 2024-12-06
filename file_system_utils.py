import os
import pygame


def save_configuration(folder_path, current_date, state):
    filename = f"initial_configuration_{current_date}.txt"
    file_path = os.path.join(folder_path, filename)

    os.makedirs(folder_path, exist_ok=True)

    with open(file_path, 'w') as file:
        for cell, state_value in state.items():
            if state_value == 1 or state_value == 2 or state_value == 3 or state_value == -1:
                q, r = cell
                file.write(f"{q},{r}\n")
                file.write(f"{state_value}\n")


def load_configuration(file_path, state):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    for i in range(0, len(lines), 2):
        coord_line = lines[i].strip()
        state_line = lines[i + 1].strip()

        q, r = map(int, coord_line.split(','))

        state_value = int(state_line)

        state[(q, r)] = state_value


def save_screenshot(screenshot_folder, counters, current_date, screen):
    screenshot_folder_path = f"screenshot_folder_{current_date}"
    full_path = os.path.join(screenshot_folder, screenshot_folder_path)

    os.makedirs(full_path, exist_ok=True)

    file_path = os.path.join(full_path, f"screenshot_{counters.turn_count}.png")

    pygame.image.save(screen, file_path)
