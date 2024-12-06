import pygame
import math as m
import sys
import os
import datetime
import simulation_utils as su
import grid_utils as gu
import file_system_utils as fsu

# PyGame base variables:

WIDTH, HEIGHT = 1800, 1400
FPS = 30

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 24)


# Simulation variables:

CELL_RADIUS = 1
radius = 150

grid = gu.generate_hex_grid(radius)
state = {cell: 0 for cell in grid}

single_turn_mode = False
show_borderline = True

C = su.Counters()
IW = su.InformationalWave()
BC = su.BorderlineCells()

GC = gu.Grid_Colors

# File system:

current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

SAVE_PATH = "data_of_initial_configurations"
LOAD_PATH = "data_of_initial_configurations/initial_configuration_2024-12-06_01-18-50.txt"

data_folder_path = "data_of_grids"
screenshot_folder = "grid_screenshots"

full_data_file_path = os.path.join(data_folder_path, f"data_{current_date}.csv")

screenshot_interval = 1

os.makedirs(data_folder_path, exist_ok=True)
os.makedirs(screenshot_folder, exist_ok=True)

###

with open(full_data_file_path, 'w') as data:
    data.write(
        f"turn_count; "
        f"active_cells_count; dead_cells_count; "
        f"first_count; second_count; third_count; "
        f"density; density1; density2; density3; "
        f"borderline_cells_count; borderline_cyan; borderline_yellow; borderline_white; borderline_black; "
        f"info_wave; blue_info_wave; red_info_wave; borderline_white; "
        f"untouched_cells_count; \n")

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
                    simulation_started = False
                    state = {cell: 0 for cell in grid}
                    C.turn_count = 0
                    next_record_turn = 0
                if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    fsu.save_configuration(SAVE_PATH, current_date, state)
                if event.key == pygame.K_l and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    fsu.load_configuration(LOAD_PATH, state)
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
            color = su.colors.get(state_value, GC.GRAY)
            if color == GC.GRAY:
                neighbors = gu.get_neighbors(cell)
                type1 = sum(state.get(neighbor, 0) == 1 for neighbor in neighbors)
                type2 = sum(state.get(neighbor, 0) == 2 for neighbor in neighbors)
                type3 = sum(state.get(neighbor, 0) == 3 for neighbor in neighbors)
                color = (255/2 + 20 * type2, 255/2 + 20 * type3, 255/2 + 20 * type1)
                if type1 != 0:
                    IW.blue_info_wave.append(cell)
                if type2 != 0:
                    IW.red_info_wave.append(cell)
                if type3 != 0:
                    IW.white_info_wave.append(cell)
                if type1 != 0 or type2 != 0 or type3 != 0:
                    IW.informational_wave_cells.append(cell)
            if state_value == 0 and cell not in IW.informational_wave_cells:
                IW.untouched_cells.append(cell)
            gu.draw_hexagon(CELL_RADIUS, screen, color, (x, y))

        if simulation_started or single_turn_mode:
            C.first_count = 0
            C.second_count = 0
            C.third_count = 0
            su.update_state(state, C)
            C.turn_count += 1

            if show_borderline:
                su.update_borderline_color(grid, state, BC, screen, CELL_RADIUS, WIDTH, HEIGHT)

            IW.info_wave_len.append(len(IW.informational_wave_cells))
            IW.untouched_cells_len.append(len(IW.untouched_cells))

            IW.informational_wave_cells.clear()
            IW.untouched_cells.clear()

            if single_turn_mode:
                single_turn_mode = False
                simulation_started = False

            single_turn_mode = su.check_for_death(state)

            if C.turn_count % screenshot_interval == 0:
                fsu.save_screenshot(screenshot_folder, C, current_date, screen)

            C.active_cells_count = C.first_count + C.second_count + C.third_count
            C.dead_cells_count = len(grid) - C.active_cells_count

            C.density = C.active_cells_count / len(grid)

            density1 = C.first_count / len(grid)
            density2 = C.second_count / len(grid)
            density3 = C.third_count / len(grid)

            data.write(
                f"{C.turn_count}; "
                f"{C.active_cells_count}; {C.dead_cells_count}; "
                f"{C.first_count}; {C.second_count}; {C.third_count}; "
                f"{C.density}; {density1}; {density2}; {density3}; "
                f"{len(su.borderline_cells(grid, state))}; "
                f"{len(BC.cyan_borderline_cells)}; "
                f"{len(BC.yellow_borderline_cells)}; "
                f"{len(BC.white_borderline_cells)}; "
                f"{len(BC.black_borderline_cells)}; "
                f"{IW.info_wave_len[C.turn_count - 1]}; "
                f"{len(IW.blue_info_wave)}; {len(IW.red_info_wave)}; {len(IW.white_info_wave)};"
                f"{IW.untouched_cells_len[C.turn_count - 1]}; \n")

        info_text = (
            f"Turns: {C.turn_count}  |  "
            f"Active Cells: {C.active_cells_count}  -  "
            f"{C.first_count}  -  {C.second_count}  -  {C.third_count}  |  "  
            f"Dead Cells: {C.dead_cells_count}  |  "
            f"Density: {C.density}  -  "
            f"  {C.first_count / len(grid)}  -  {C.second_count / len(grid)}  -  {C.third_count / len(grid)}")
        info_surface = font.render(info_text, True, GC.BLACK)

        text_width, text_height = info_surface.get_size()

        screen.blit(info_surface, ((WIDTH - text_width) // 10, (HEIGHT - text_height) // 6))

        pygame.display.flip()
        clock.tick(FPS)

pygame.quit()
