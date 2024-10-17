import pygame
import math as m
import sys
import datetime
import os

"""
შეტყობინება ბატონი გრიგოლისთვის:

    SPACE - სიმულაციის დაწყება
    r - სიბრტყის გასუფთავება(არესტარდებს სიმულაციას)
    p - single_turn_mode-ის ჩართვა(ბიჯი-ბიჯი, ასევე ვიყენებთ ამას როგორც პაუზას)

    (ცნობისთვის single_turn_mode ირთვება როცა ერთ-ერთი ცივილიზაცია მაინც კვდება(ასე გავაკეთე მაგის რეალიზაცია))

    CTRL + s - მიმდინარე კონფიგურაციის დამახსოვრება(იმახსოვრებს კონფიგურაციას ტექსტურ ფაილში)
    CTRL + l - დამახსოვრებული კონფიგურაციის მითითების შემდეგ(LOAD_PATH) მისი ატვირთვის საშუალებას გვაძლევს

    h - ამ ღილაკით შეიძლება დამალო/გამოაჩინო ეგ შავი საზღვარი
"""

# Настройки конфигурации:
SAVE_PATH = "data_of_initial_configurations"
LOAD_PATH = "data_of_initial_configurations/initial_configuration_2024-10-15_22-13-39.txt"

# Настройки экрана
WIDTH, HEIGHT = 1800, 1400
FPS = 30
CELL_RADIUS = 15
radius = 3

COLOR_D = 40

# Цвета
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Определите цвета для каждого состояния
colors = {
    0: GRAY,
    1: BLUE,
    2: RED
}

# Счётчики
turn_count = 0
active_cells_count = 0
first_count = 0
second_count = 0
dead_cells_count = 0
density = 0

# Модификации
single_turn_mode = False
show_borderline = True

# Дата
current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 24)

# Вычисление расстояний между шестиугольниками
dx = 3 / 2 * CELL_RADIUS
dy = m.sqrt(3) * CELL_RADIUS


# Генерация шестиугольной сетки
def generate_hex_grid(radius):
    grid = []
    for q in range(-radius, radius + 1):
        for r in range(-radius, radius + 1):
            if abs(q + r) <= radius:
                grid.append((q, r))
    return grid


def hex_to_pixel(q, r):
    x = CELL_RADIUS * (3 / 2 * q)
    y = CELL_RADIUS * (m.sqrt(3) * (r + q / 2))
    return int(x + WIDTH // 2), int(y + HEIGHT // 2)


def draw_hexagon(surface, color, pos):
    x, y = pos
    points = []
    for i in range(6):
        angle = m.pi / 3 * i
        point_x = x + CELL_RADIUS * m.cos(angle)
        point_y = y + CELL_RADIUS * m.sin(angle)
        points.append((point_x, point_y))
    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, GRAY, points, 1)


def get_neighbors(cell):
    q, r = cell
    directions = [
        (1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)
    ]
    return [(q + dq, r + dr) for dq, dr in directions]


# Инициализация состояния ячеек
grid = generate_hex_grid(radius)
state = {cell: 0 for cell in grid}


def update_state():
    global state
    global first_count
    global second_count

    new_state = state.copy()  # Create a copy for updates

    for cell in state:
        neighbors = get_neighbors(cell)

        # Count neighbors of different states
        type1_neighbors = sum(state.get(neighbor, 0) == 1 for neighbor in neighbors)
        type2_neighbors = sum(state.get(neighbor, 0) == 2 for neighbor in neighbors)

        alive_neighbors = sum(state.get(neighbor, 0) > 0 for neighbor in neighbors)

        current_state = state[cell]
        new_state[cell] = 0  # Dies

        if current_state == 0 and type1_neighbors * type2_neighbors != 0:
            if type1_neighbors > type2_neighbors:
                new_state[cell] = 1
                first_count = first_count + 1
            if type1_neighbors < type2_neighbors:
                new_state[cell] = 2
                second_count = second_count + 1

        if current_state == 0 and type1_neighbors * type2_neighbors == 0:
            if type1_neighbors > type2_neighbors and (type1_neighbors == 2 or type1_neighbors == 3):
                new_state[cell] = 1
                first_count = first_count + 1
            if type1_neighbors < type2_neighbors and (type2_neighbors == 2 or type2_neighbors == 3):
                new_state[cell] = 2
                second_count = second_count + 1

        if current_state == 1 and (type1_neighbors == 2 or type1_neighbors == 3):
            new_state[cell] = 1  # Become type 1
            first_count = first_count + 1
        if current_state == 2 and (type2_neighbors == 2 or type2_neighbors == 3):
            new_state[cell] = 2  # Become type 2
            second_count = second_count + 1

    state = new_state  # Apply the new state


def borderline_cells():
    borderline = []
    for cell in grid:
        neighbors = get_neighbors(cell)
        type1_neighbors = sum(state.get(neighbor, 0) == 1 for neighbor in neighbors)
        type2_neighbors = sum(state.get(neighbor, 0) == 2 for neighbor in neighbors)
        dead_neighbors = sum(state.get(neighbor, 0) == 0 for neighbor in neighbors)

        # If cell is dead and has at least one of each type around it
        if state[cell] == 0 and type1_neighbors > 0 and type2_neighbors > 0:
            borderline.append(cell)
        # If cell is type 1 or 2 and has both other types as neighbors
        elif (state[cell] == 1 and type2_neighbors > 0 and dead_neighbors > 0) or (
                state[cell] == 2 and type1_neighbors > 0 and dead_neighbors > 0):
            borderline.append(cell)

    return borderline


def update_borderline_color():
    borderline = borderline_cells()
    for cell in borderline:
        q, r = hex_to_pixel(*cell)

        draw_hexagon(screen, BLACK, (q, r))


# Linear Interpolation (Lerp) functions:

def diagonal_distance(start_cell, end_cell):
    dq, dr = start_cell[0] - end_cell[0], start_cell[1] - end_cell[1]
    return max(abs(dq), abs(dr))


def round_cell(cell):
    q, r = cell
    return round(q), round(r)


def lerp(start, end, t):
    return start * (1.0 - t) + end * t


def lerp_point(start_cell, end_cell, t):
    q0 = start_cell[0]
    q1 = end_cell[0]
    r0 = start_cell[1]
    r1 = end_cell[1]
    return lerp(q0, q1, t), lerp(r0, r1, t)


def borderline_length(start_cell, end_cell):
    cells = []
    N = diagonal_distance(start_cell, end_cell)
    for step in range(0, N + 1):
        t = step / N if N != 0 else 0
        lerped_point = lerp_point(start_cell, end_cell, t)
        cells.append(round_cell(lerped_point))
    return cells


def paint_line(start_cell, end_cell):
    borderline = borderline_length(start_cell, end_cell)
    for cell in borderline:
        q, r = hex_to_pixel(*cell)
        draw_hexagon(screen, BLACK, (q, r))


def check_for_death():
    global state
    global single_turn_mode

    type1 = sum(state.get(cell, 0) == 1 for cell in state)
    type2 = sum(state.get(cell, 0) == 2 for cell in state)

    if type1 == 0 or type2 == 0:
        single_turn_mode = True


def get_informational_wave():
    global state

    informational_cells = []

    for cell in grid:
        get_state = state[cell]
        get_color = colors.get(get_state, GRAY)
        if get_color == GRAY:
            neighbors = get_neighbors(cell)
            type1 = sum(state.get(neighbor, 0) == 1 for neighbor in neighbors)
            type2 = sum(state.get(neighbor, 0) == 2 for neighbor in neighbors)
            if type1 != 0 or type2 != 0:
                print(cell)
                informational_cells.append(cell)

    return informational_cells


def get_alive_cells():
    global state
    alive_cells = []
    for cell in grid:
        if state[cell] != 0:
            alive_cells.append(cell)
    return alive_cells


def get_untouched_cells():
    global state
    global grid

    untouched_cells = []

    for cell in state:
        if state[cell] == 0 and cell not in get_informational_wave():
            untouched_cells.append(cell)

    return untouched_cells


def save_configuration(folder_path):
    filename = f"initial_configuration_{current_date}.txt"
    file_path = os.path.join(folder_path, filename)

    # Создаем папку, если она не существует
    os.makedirs(folder_path, exist_ok=True)

    with open(file_path, 'w') as file:
        for cell, state_value in state.items():
            if state_value == 1 or state_value == 2:  # Сохраняем только живые клетки
                q, r = cell
                file.write(f"{q},{r}\n")
                file.write(f"{state_value}\n")  # Сохраняем значение состояния (0 или 1)


def load_configuration(file_path):
    global state

    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Пробегаем по строкам и обновляем состояние
    for i in range(0, len(lines), 2):  # Читаем каждую пару строк (координаты и состояние)
        coord_line = lines[i].strip()
        state_line = lines[i + 1].strip()

        # Преобразуем строку координат в кортеж целых чисел
        q, r = map(int, coord_line.split(','))

        # Преобразуем строку состояния в целое число
        state_value = int(state_line)

        # Обновляем состояние
        state[(q, r)] = state_value


def save_screenshot(screen, turn_count, screenshot_folder):
    screenshot_folder_path = f"screenshot_folder_{current_date}"
    full_path = os.path.join(screenshot_folder, screenshot_folder_path)

    os.makedirs(full_path, exist_ok=True)  # Создаем папку, если она не существует

    file_path = os.path.join(full_path, f"screenshot_{turn_count}.png")

    pygame.image.save(screen, file_path)


def saving_borderline_length(file_path):
    with open(file_path, "a") as file:
        file.write(f"{turn_count}, {len(borderline_cells())}\n")


def saving_informational_wave(file_path):
    with open(file_path, "a") as file:
        file.write(f"{turn_count}, {len(get_informational_wave())}\n")


def saving_untouched_cells(file_path):
    with open(file_path, "a") as file:
        file.write(f"{turn_count}, {len(get_untouched_cells())}\n")


# Пути к папкам
folder_path = "data_of_grids"
screenshot_folder = "grid_screenshots"
borderline_len = "borderline_length"
info_wave_folder = "informational_wave"
untouched_cells_folder = "untouched_cells"

info_wave_file = os.path.join(info_wave_folder, f"informational_wave_{current_date}.txt")
borderline_len_file = os.path.join(borderline_len, f"borderline_length_{current_date}.txt")
untouched_cells_file = os.path.join(untouched_cells_folder, f"untouched_cells_{current_date}.txt")

file_path = os.path.join(folder_path, f"data_{current_date}.csv")

screenshot_interval = 1  # Интервал для сохранения скриншотов

os.makedirs(folder_path, exist_ok=True)
os.makedirs(screenshot_folder, exist_ok=True)

# Открытие файла для записи данных
with open(file_path, 'w') as data:
    # Основной игровой цикл
    data.write(
        f"turn_count; active_cells_count; dead_cells_count; first_count; second_count; density; density1; density2\n")
    running = True
    simulation_started = False
    record_interval = 1  # Интервал записи данных (1 шаг)
    next_record_turn = 0

    # Основной игровой цикл
    while running:
        screen.fill(WHITE)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not simulation_started:
                pos = pygame.mouse.get_pos()
                for cell in grid:
                    x, y = hex_to_pixel(*cell)
                    if m.dist(pos, (x, y)) < CELL_RADIUS:
                        state[cell] = (state[cell] + 1) % 3  # Переключение состояния циклически. % на кол. состояний!
                        # print(cell)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    simulation_started = True
                if event.key == pygame.K_p:
                    single_turn_mode = True
                if event.key == pygame.K_h:
                    show_borderline = not show_borderline
                if event.key == pygame.K_r:
                    state = {cell: 0 for cell in grid}  # Сброс на 0
                    simulation_started = False
                    turn_count = 0
                    next_record_turn = 0
                if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    save_configuration(SAVE_PATH)
                if event.key == pygame.K_l and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    load_configuration(LOAD_PATH)
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        for cell in grid:
            x, y = hex_to_pixel(*cell)
            state_value = state[cell]
            color = colors.get(state_value, GRAY)  # Если состояние не найдено, используем серый цвет
            if color == GRAY:
                neighbors = get_neighbors(cell)
                type1 = sum(state.get(neighbor, 0) == 1 for neighbor in neighbors)
                type2 = sum(state.get(neighbor, 0) == 2 for neighbor in neighbors)
                color = (255 - COLOR_D * type2, 255 / 2 + 20 * (type1 + type2), COLOR_D * type1)
                # CD = COLOR_D, CD * type2 + CD * type1
            draw_hexagon(screen, color, (x, y))

        if show_borderline:
            update_borderline_color()

        # Обновление состояния только при запущенной симуляции
        if simulation_started or single_turn_mode:
            first_count = 0
            second_count = 0
            update_state()
            turn_count += 1

            check_for_death()

            saving_borderline_length(borderline_len_file)
            saving_informational_wave(info_wave_file)
            saving_untouched_cells(untouched_cells_file)

            if single_turn_mode:
                single_turn_mode = False
                simulation_started = False

            # Сохранение скриншота каждые screenshot_interval шагов
            if turn_count % screenshot_interval == 0:
                pass
                save_screenshot(screen, turn_count, screenshot_folder)

            # Количество активных, мёртвых и общих клеток:
            active_cells_count = first_count + second_count
            dead_cells_count = len(grid) - active_cells_count

            density = active_cells_count / len(grid)

            density1 = first_count / len(grid)
            density2 = second_count / len(grid)

            data.write(
                f"{turn_count}; {active_cells_count}; {dead_cells_count}; {first_count}; {second_count}; {density}; {density1}; {density2}\n")

            # Запись данных в текстовый файл каждые record_interval шагов
            if turn_count >= next_record_turn:
                if turn_count <= 10:
                    pass
                next_record_turn += record_interval

        # Отображение счётчиков
        screen_width = WIDTH
        screen_height = HEIGHT
        info_text = f"Turns: {turn_count}  |  Active Cells: {active_cells_count}  -  {first_count}  -  {second_count}  |  Dead Cells: {dead_cells_count} | Density: {density}  -  {first_count / len(grid)}  -  {second_count / len(grid)}"
        info_surface = font.render(info_text, True, BLACK)

        text_width, text_height = info_surface.get_size()

        screen.blit(info_surface, ((screen_width - text_width) // 10, (screen_height - text_height) // 6))

        # Обновление экрана
        pygame.display.flip()
        clock.tick(FPS)

pygame.quit()
