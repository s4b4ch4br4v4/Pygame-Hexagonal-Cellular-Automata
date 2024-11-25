from dataclasses import dataclass
from dataclasses import field
import grid_utils as gu

colors = {
    -1: gu.Grid_Colors.DARK_GRAY,
    0: gu.Grid_Colors.GRAY,
    1: gu.Grid_Colors.BLUE,
    2: gu.Grid_Colors.RED,
    3: gu.Grid_Colors.GREEN
}


@dataclass
class Counters:
    turn_count: int = field(default=0)
    active_cells_count: int = field(default=0)
    dead_cells_count: int = field(default=0)
    first_count: int = field(default=0)
    second_count: int = field(default=0)
    density: float = field(default=0.0)


@dataclass
class InformationalWave:
    informational_wave_cells: list = field(default_factory=list)
    blue_info_wave: list = field(default_factory=list)
    red_info_wave: list = field(default_factory=list)
    untouched_cells: list = field(default_factory=list)
    info_wave_len: list = field(default_factory=list)
    untouched_cells_len: list = field(default_factory=list)


@dataclass
class BorderlineCells:
    cyan_borderline_cells: set = field(default_factory=set)
    yellow_borderline_cells: set = field(default_factory=set)
    black_borderline_cells: set = field(default_factory=set)


def update_state(state, counters):
    new_state = state.copy()

    for cell in new_state:
        if new_state[cell] != -1:
            neighbors = gu.get_neighbors(cell)

            type1_neighbors = sum(state.get(neighbor, 0) == 1 for neighbor in neighbors)
            type2_neighbors = sum(state.get(neighbor, 0) == 2 for neighbor in neighbors)

            current_state = state[cell]
            new_state[cell] = 0

            if current_state == 0 and type1_neighbors * type2_neighbors != 0:
                if type1_neighbors > type2_neighbors:
                    new_state[cell] = 1
                    counters.first_count += 1
                elif type1_neighbors < type2_neighbors:
                    new_state[cell] = 2
                    counters.second_count += 1

            elif current_state == 0 and type1_neighbors * type2_neighbors == 0:
                if type1_neighbors > type2_neighbors and (type1_neighbors == 2 or type1_neighbors == 3):
                    new_state[cell] = 1
                    counters.first_count += 1
                elif type1_neighbors < type2_neighbors and (type2_neighbors == 2 or type2_neighbors == 3):
                    new_state[cell] = 2
                    counters.second_count += 1

            elif current_state == 1 and (type1_neighbors == 2 or type1_neighbors == 3):
                new_state[cell] = 1
                counters.first_count += 1
            elif current_state == 2 and (type2_neighbors == 2 or type2_neighbors == 3):
                new_state[cell] = 2
                counters.second_count += 1

    state.clear()
    state.update(new_state)


def borderline_cells(grid, state):
    borderline = []
    for cell in grid:
        neighbors = gu.get_neighbors(cell)
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


def update_borderline_color(grid, state, BC, screen, CELL_RADIUS, WIDTH, HEIGHT):
    BC.cyan_borderline_cells.clear()
    BC.yellow_borderline_cells.clear()
    BC.black_borderline_cells.clear()

    borderline = borderline_cells(grid, state)
    for cell in borderline:
        neighbors = gu.get_neighbors(cell)

        type1_neighbors = sum(state.get(neighbor, 0) == 1 for neighbor in neighbors)
        type2_neighbors = sum(state.get(neighbor, 0) == 2 for neighbor in neighbors)

        q, r = gu.hex_to_pixel(CELL_RADIUS, WIDTH, HEIGHT, *cell)

        if type1_neighbors > type2_neighbors:
            BC.cyan_borderline_cells.add(cell)
            gu.draw_hexagon(CELL_RADIUS, screen, gu.Grid_Colors.CYAN, (q, r))
        elif type1_neighbors < type2_neighbors:
            BC.yellow_borderline_cells.add(cell)
            gu.draw_hexagon(CELL_RADIUS, screen, gu.Grid_Colors.YELLOW, (q, r))
        else:
            BC.black_borderline_cells.add(cell)
            gu.draw_hexagon(CELL_RADIUS, screen, gu.Grid_Colors.BLACK, (q, r))


def check_for_death(state):
    type1 = sum(state.get(cell, 0) == 1 for cell in state)
    type2 = sum(state.get(cell, 0) == 2 for cell in state)

    if type1 == 0 or type2 == 0:
        return True
