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
LOAD_PATH = "data_of_initial_configurations/initial_configuration_2024-10-23_14-40-11.txt"

# Настройки экрана
WIDTH, HEIGHT = 1800, 1400
FPS = 30
CELL_RADIUS = 5
radius = 50

# Дифференциал цвета
COLOR_D = 40

# Цвета
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)

# Определите цвета для каждого состояния
colors = {
    0: GRAY,
    1: BLUE,
    2: RED,
    -1: DARK_GRAY
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

# Клетки информационные и нетронутые
informational_wave_cells = []
blue_info_wave = []
red_info_wave = []
untouched_cells = []

info_wave_len = []
untouched_cells_len = []

# Клетки границы:
cyan_borderline_cells = set()
yellow_borderline_cells = set()
black_borderline_cells = set()

# Текущая дата
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


# Конвертация в пиксельные координаты монитора
def hex_to_pixel(q, r):
    x = CELL_RADIUS * (3 / 2 * q)
    y = CELL_RADIUS * (m.sqrt(3) * (r + q / 2))
    return int(x + WIDTH // 2), int(y + HEIGHT // 2)


# Рисование шестиугольника
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


# Вычисление соседей
def get_neighbors(cell):
    q, r = cell
    directions = [
        (1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)
    ]
    return [(q + dq, r + dr) for dq, dr in directions]


# Инициализация состояния ячеек
grid = generate_hex_grid(radius)
state = {cell: 0 for cell in grid}


# Условия среды
def update_state():
    global state
    global first_count
    global second_count

    new_state = state.copy()  # Create a copy for updates

    for cell in state:
        if state[cell] != -1:
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


# Вычисление граничных клеток
def borderline_cells():
    borderline = []
    for cell in grid:
        neighbors = get_neighbors(cell)
        type1_neighbors = sum(state.get(neighbor, 0) == 1 for neighbor in neighbors)
        type2_neighbors = sum(state.get(neighbor, 0) == 2 for neighbor in neighbors)
        dead_neighbors = sum(state.get(neighbor, 0) == 0 for neighbor in neighbors)

        if state[cell] == 0 and type1_neighbors * type2_neighbors * dead_neighbors != 0:
            borderline.append(cell)
        elif state[cell] == 1 and type1_neighbors * type2_neighbors * dead_neighbors != 0:
            borderline.append(cell)
        elif state[cell] == 2 and type1_neighbors * type2_neighbors * dead_neighbors != 0:
            borderline.append(cell)

    return borderline


# Измененеие их цвета а так же добывает определённые типы граничных клеток
def update_borderline_color():
    cyan_borderline_cells.clear()
    yellow_borderline_cells.clear()
    black_borderline_cells.clear()

    borderline = borderline_cells()
    for cell in borderline:
        neighbors = get_neighbors(cell)

        type1_neighbors = sum(state.get(neighbor, 0) == 1 for neighbor in neighbors)
        type2_neighbors = sum(state.get(neighbor, 0) == 2 for neighbor in neighbors)

        q, r = hex_to_pixel(*cell)

        if type1_neighbors > type2_neighbors:
            cyan_borderline_cells.add(cell)
            draw_hexagon(screen, CYAN, (q, r))
        elif type1_neighbors < type2_neighbors:
            yellow_borderline_cells.add(cell)
            draw_hexagon(screen, YELLOW, (q, r))
        else:
            black_borderline_cells.add(cell)
            draw_hexagon(screen, BLACK, (q, r))


# Поверка на смерть типа клеток чтобы остановить симуляцию
def check_for_death():
    global state
    global single_turn_mode

    type1 = sum(state.get(cell, 0) == 1 for cell in state)
    type2 = sum(state.get(cell, 0) == 2 for cell in state)

    if type1 == 0 or type2 == 0:
        single_turn_mode = True


# Сохраняет позиции клеток в файл которые после можно установить как начальная конфигурация
def save_configuration(folder_path):
    filename = f"initial_configuration_{current_date}.txt"
    file_path = os.path.join(folder_path, filename)

    # Создаем папку, если она не существует
    os.makedirs(folder_path, exist_ok=True)

    with open(file_path, 'w') as file:
        for cell, state_value in state.items():
            if state_value == 1 or state_value == 2 or state_value == -1:  # Сохраняем только живые клетки
                q, r = cell
                file.write(f"{q},{r}\n")
                file.write(f"{state_value}\n")  # Сохраняем значение состояния (0 или 1)


# Установка начальной конфигурации
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


# Каждый шаг делает скриншот
def save_screenshot(screen, turn_count, screenshot_folder):
    screenshot_folder_path = f"screenshot_folder_{current_date}"
    full_path = os.path.join(screenshot_folder, screenshot_folder_path)

    os.makedirs(full_path, exist_ok=True)  # Создаем папку, если она не существует

    file_path = os.path.join(full_path, f"screenshot_{turn_count}.png")

    pygame.image.save(screen, file_path)


# Пути к папкам
folder_path = "data_of_grids"
screenshot_folder = "grid_screenshots"

file_path = os.path.join(folder_path, f"data_{current_date}.csv")

screenshot_interval = 1  # Интервал для сохранения скриншотов

os.makedirs(folder_path, exist_ok=True)
os.makedirs(screenshot_folder, exist_ok=True)

# Открытие файла для записи данных
with open(file_path, 'w') as data:
    # Основной игровой цикл
    data.write(
        f"turn_count; active_cells_count; dead_cells_count; first_count; second_count; density; density1; density2; borderline_cells_count; borderline_cyan; borderline_yellow; borderline_black; info_wave; blue_info_wave; red_info_wave; untouched_cells_count;\n")
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
                        if event.button == 1:
                            state[cell] = (state[cell] + 1) % 3  # Переключение между 0, 1, 2 для обычных клеток
                        elif event.button == 3:
                            if state[cell] == -1:
                                state[cell] = 0
                            else:
                                state[cell] = -1
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

        informational_wave_cells.clear()
        blue_info_wave.clear()
        red_info_wave.clear()

        for cell in grid:
            x, y = hex_to_pixel(*cell)
            state_value = state[cell]
            color = colors.get(state_value, GRAY)  # Если состояние не найдено, используем серый цвет
            if color == GRAY:
                info_wave = []
                neighbors = get_neighbors(cell)
                type1 = sum(state.get(neighbor, 0) == 1 for neighbor in neighbors)
                type2 = sum(state.get(neighbor, 0) == 2 for neighbor in neighbors)
                color = (255 - COLOR_D * type2, 255 / 2 + 20 * (type1 + type2), COLOR_D * type1)
                # CD = COLOR_D, CD * type2 + CD * type1
                if type1 != 0:
                    blue_info_wave.append(cell)
                if type2 != 0:
                    red_info_wave.append(cell)
                if type1 != 0 or type2 != 0:
                    informational_wave_cells.append(cell)
            if state_value == 0 and cell not in informational_wave_cells:
                untouched_cells.append(cell)
            draw_hexagon(screen, color, (x, y))

        # Обновление состояния только при запущенной симуляции
        if simulation_started or single_turn_mode:
            first_count = 0
            second_count = 0
            update_state()
            turn_count += 1

            if show_borderline:
                update_borderline_color()

            info_wave_len.append(len(informational_wave_cells))
            untouched_cells_len.append(len(untouched_cells))

            informational_wave_cells.clear()
            untouched_cells.clear()

            check_for_death()

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
                f"{turn_count}; {active_cells_count}; {dead_cells_count}; {first_count}; {second_count}; {density}; {density1}; {density2}; {len(borderline_cells())}; {len(cyan_borderline_cells)}; {len(yellow_borderline_cells)}; {len(black_borderline_cells)}; {len(informational_wave_cells)}; {len(blue_info_wave)}; {len(red_info_wave)}; {untouched_cells_len[turn_count-1]};\n")

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