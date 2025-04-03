import pygame
import math as m
import sys
import os
import datetime
import simulation_utils as su
import grid_utils as gu
import file_system_utils as fsu
import file_system_gui as fsg

"""
შეტყობინება ბატონი გრიგოლისთვის:
    RMB, LMB - უჯრისა და კედლის დასმა
    SPACE - სიმულაციის დაწყება
    R - სიბრტყის გასუფთავება(არესტარდებს სიმულაციას)
    P - single_turn_mode-ის ჩართვა(ბიჯი-ბიჯი, ასევე ვიყენებთ ამას როგორც პაუზას)
    CTRL + S - მიმდინარე კონფიგურაციის დამახსოვრება(იმახსოვრებს კონფიგურაციას ტექსტურ ფაილში)
    CTRL + L - დამახსოვრებული კონფიგურაციის მითითების შემდეგ(LOAD_PATH) მისი ატვირთვის საშუალებას გვაძლევს
    H - ამ ღილაკით შეიძლება დამალო/გამოაჩინო ეგ შავი საზღვარი
    O - უჯრედებისაგან ექვსკუთხედების ხატვა(hex_click_mode)
    G - გენერაცია შემთხვევით ადგილას ყველა ტიპის უჯრისაგან ექვსკუთხედის
    D - უჯრების გადარჩენის ჩართვა/გათიშვა(მარჯვენა ზედა კუთხეში ინდიკატორიც კი არის)
    
    !!! უჯრების გადარჩენის კონტროლი აქტუალურია როცა სიმულაცია მუშაობს ჩვენი სისტემით !!!
    !!! რადგან მათ სისტემაში არ არის გათვალისწინებული უჯრების თავისით სიკვდილიანობა !!!
    !!! ასევე, სიმულაციის მთელი ფუნქციონალი კორექტულად არ მუშაობს მათ სისტემასთან !!!
"""

# PyGame base variables:

WIDTH, HEIGHT = 1700, 900
FPS = 30

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Hexagonal Grid Simulation")  # Sets the window title
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 24)

# Simulation variables:

"""rules და threshold არ არის ჩვენი სისტემის ნაწილი"""

"""
    წესები(rules) მუშაობენ следующим образом:
    დიქტში გასაღები არის უჯრის ტიპი, ხოლო
    მნიშვნელობად ლისტში არის მითითებული ის უჯრის ტიპები, რომლებსაც
    შეუძლიათ მაგ უჯრის ჭამა.
    {"მე": ["ვინ მჭამს მე"]}
    0-ის ჭამა ყველას შეუძლია, 1-ს ჭამს 3 და ა.შ.
"""
rules = {0: [1, 2, 3], 1: [3], 2: [1], 3: [2]}

"""
    threshold(порог, ზღურბლი) არის საჭირო სამეზობლოში საჭირო მტრების რაოდენობა, რომ
    შეიჭამოს გარკვეული ტიპის უჯრა, რომლის ჭამაც შეუძლია მტერს.
    მაგალითად: 1 ტიპის უჯრა რომ შეჭამოს 3 ტიპის უჯრამ(რადგან, ვიცით 1: [3])
    1 ტიპის უჯრის ირგვლივ 3 ტიპის უჯრების რაოდენობა უნდა იყოს მოცემულ სეგმენტში [2, 4].
"""
threshold = [2, 3]
# threshold = {0: [1, 2, 3], 1: [3], 2: [1], 3: [2,5]}
CELL_RADIUS = 10
radius = 20

grid = gu.generate_hex_grid(radius)
state = {cell: 0 for cell in grid}

single_turn_mode = False
show_borderline = False
hex_click_mode = False
highlighted_cell = None
initial_counts = None

C = su.Counters()
IW = su.InformationalWave()
BC = su.BorderlineCells()

GC = gu.Grid_Colors

# File system:

current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

SAVE_PATH = "data_of_initial_configurations"
LOAD_PATH = ""

data_folder_path = "data_of_grids"
screenshot_folder = "grid_screenshots"

full_data_file_path = os.path.join(data_folder_path, f"data_{current_date}.csv")

screenshot_interval = 1

os.makedirs(data_folder_path, exist_ok=True)
os.makedirs(screenshot_folder, exist_ok=True)

###

with open(full_data_file_path, 'w') as data:
    data.write(
        f"turn_count;"
        f"active_cells_count;dead_cells_count;"
        f"first_count;second_count;third_count;"
        f"density;density1;density2;density3;"
        f"borderline_cells_count;borderline_cyan;borderline_yellow;borderline_white;borderline_black;"
        f"info_wave;blue_info_wave;red_info_wave;green_info_wave;"
        f"untouched_cells_count;\n")

    running = True
    simulation_started = False
    record_interval = 1

    while running:
        screen.fill(GC.WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not simulation_started:
                pos = pygame.mouse.get_pos()
                for cell in grid:
                    x, y = gu.hex_to_pixel(CELL_RADIUS, WIDTH, HEIGHT, *cell)
                    if m.dist(pos, (x, y)) < CELL_RADIUS:
                        if event.button == 1:
                            state[cell] = (state[cell] + 1) % 4
                        if event.button == 1 and hex_click_mode:
                            su.state_neighborhood(state, cell)
                        if event.button == 3:
                            if state[cell] == -1:
                                state[cell] = 0
                            else:
                                state[cell] = -1
            elif event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                for cell in grid:
                    x, y = gu.hex_to_pixel(CELL_RADIUS, WIDTH, HEIGHT, *cell)
                    if m.dist(pos, (x, y)) < CELL_RADIUS:
                        highlighted_cell = cell
                        break
                else:
                    highlighted_cell = None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    simulation_started = not simulation_started
                    show_borderline = True
                    if initial_counts is None:
                        initial_counts = su.analyze_grid(state)
                if event.key == pygame.K_p:
                    single_turn_mode = not single_turn_mode
                if event.key == pygame.K_o:
                    hex_click_mode = not hex_click_mode
                if event.key == pygame.K_d:
                    su.survival = not su.survival
                if event.key == pygame.K_h:
                    show_borderline = not show_borderline
                if event.key == pygame.K_r:
                    simulation_started = False
                    state = {cell: 0 for cell in grid}
                    C.turn_count = 0
                    next_record_turn = 0
                if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    fsu.save_configuration(SAVE_PATH, current_date, state)
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                if event.key == pygame.K_g:
                    su.generate_rand_config(grid, state, radius-15)
                if event.key == pygame.K_l and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    simulation_started = False
                    state = {cell: 0 for cell in grid}
                    C.turn_count = 0
                    next_record_turn = 0
                    selected_file = fsg.select_file(SAVE_PATH)
                    if selected_file:
                        fsu.load_configuration(selected_file, state)
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        IW.informational_wave_cells.clear()
        IW.blue_info_wave.clear()
        IW.red_info_wave.clear()
        IW.white_info_wave.clear()

        for cell in grid:
            x, y = gu.hex_to_pixel(CELL_RADIUS, WIDTH, HEIGHT, *cell)
            state_value = state[cell]
            color = su.colors.get(state[cell], GC.GRAY)
            if color == GC.GRAY:
                neighbors = gu.get_neighbors(cell)
                type1 = sum(state.get(neighbor, 0) == 1 for neighbor in neighbors)
                type2 = sum(state.get(neighbor, 0) == 2 for neighbor in neighbors)
                type3 = sum(state.get(neighbor, 0) == 3 for neighbor in neighbors)
                color = (255 / 2 + 20 * type2, 255 / 2 + 20 * type3, 255 / 2 + 20 * type1)
                if type1 != 0:
                    IW.blue_info_wave.add(cell)
                if type2 != 0:
                    IW.red_info_wave.add(cell)
                if type3 != 0:
                    IW.white_info_wave.add(cell)
                if type1 != 0 or type2 != 0 or type3 != 0:
                    IW.informational_wave_cells.add(cell)
            if state_value == 0 and cell not in IW.informational_wave_cells:
                IW.untouched_cells.add(cell)
            gu.draw_hexagon(CELL_RADIUS, screen, color, (x, y))

        if highlighted_cell:
            highlight_color = su.colors.get(state[highlighted_cell])
            darkened_color = tuple(max(0, int(c * 0.9)) for c in highlight_color)
            x, y = gu.hex_to_pixel(CELL_RADIUS, WIDTH, HEIGHT, *highlighted_cell)
            gu.draw_hexagon(CELL_RADIUS, screen, darkened_color, (x, y))


        if simulation_started:
            simulation_started = su.check_for_death(initial_counts, state)
            C.first_count = 0
            C.second_count = 0
            C.third_count = 0

            """
                update_state - ჩვენი უჯრების მდგომარეობის განახლების სისტემა 
                update_state2 - მათი
                
                !!! მხოლოდ ერთი უნდა მუშაობდეს !!!
            """

            su.update_state(state, C)
            # su.update_state2(state, C, rules, threshold)

            su.clear_edges(state, su.precompute_edges(radius))
            C.turn_count += 1

            IW.info_wave_len.append(len(IW.informational_wave_cells))
            IW.untouched_cells_len.append(len(IW.untouched_cells))

            IW.informational_wave_cells.clear()
            IW.untouched_cells.clear()

            if single_turn_mode:
                simulation_started = False

            if C.turn_count % screenshot_interval == 0:
                fsu.save_screenshot(screenshot_folder, C, current_date, screen)

            C.active_cells_count = C.first_count + C.second_count + C.third_count
            C.dead_cells_count = len(grid) - C.active_cells_count

            C.density = C.active_cells_count / len(grid)

            density1 = C.first_count / len(grid)
            density2 = C.second_count / len(grid)
            density3 = C.third_count / len(grid)

            data.write(
                f"{C.turn_count};"
                f"{C.active_cells_count};{C.dead_cells_count};"
                f"{C.first_count};{C.second_count};{C.third_count};"
                f"{C.density};{density1};{density2};{density3};"
                f"{len(su.borderline_cells(grid, state))};"
                f"{len(BC.cyan_borderline_cells)};"
                f"{len(BC.yellow_borderline_cells)};"
                f"{len(BC.white_borderline_cells)};"
                f"{len(BC.black_borderline_cells)};"
                f"{IW.info_wave_len[C.turn_count - 1]};"
                f"{len(IW.blue_info_wave)};{len(IW.red_info_wave)};{len(IW.white_info_wave)};"
                f"{IW.untouched_cells_len[C.turn_count - 1]};\n")

        info_text1 = (
            f"Turns: {C.turn_count}  |  "
            f"Active Cells: {C.active_cells_count}  -  "
            f"{C.first_count}  -  {C.second_count}  -  {C.third_count}  |  "
            f"Dead Cells: {C.dead_cells_count}  |  "
            f"Density: {C.density}  -  "
            f"  {C.first_count / len(grid)}  -  {C.second_count / len(grid)}  -  {C.third_count / len(grid)}"
        )

        info_text2 = f"Survival: {su.survival}"

        info_surface1 = font.render(info_text1, True, GC.BLACK)
        info_surface2 = font.render(info_text2, True, GC.BLACK)

        text_width1, text_height1 = info_surface1.get_size()

        screen.blit(info_surface1, (10, 10))  # Place the first info text at (10, 10)
        screen.blit(info_surface2, (10, 40))  # Place the second info text slightly below the first

        if show_borderline:
            su.update_borderline_color(grid, state, BC, screen, CELL_RADIUS, WIDTH, HEIGHT)
        pygame.display.flip()
        clock.tick(FPS)

pygame.quit()
