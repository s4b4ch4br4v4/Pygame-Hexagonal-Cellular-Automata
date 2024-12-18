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
    third_count: int = field(default=0)
    density: float = field(default=0.0)


@dataclass
class InformationalWave:
    informational_wave_cells: list = field(default_factory=list)
    blue_info_wave: list = field(default_factory=list)
    red_info_wave: list = field(default_factory=list)
    white_info_wave: list = field(default_factory=list)
    untouched_cells: list = field(default_factory=list)
    info_wave_len: list = field(default_factory=list)
    untouched_cells_len: list = field(default_factory=list)


@dataclass
class BorderlineCells:
    cyan_borderline_cells: list = field(default_factory=list)
    yellow_borderline_cells: list = field(default_factory=list)
    white_borderline_cells: list = field(default_factory=list)
    black_borderline_cells: list = field(default_factory=list)


survival = True

type1_min, type1_max = 2, 3
type2_min, type2_max = 2, 3
type3_min, type3_max = 2, 3

typeparams = [[type1_min, type1_max], [type2_min, type2_max], [type3_min, type3_max]]


def update_counters(counters, cell_type):
    if cell_type == 1:
        counters.first_count += 1
    elif cell_type == 2:
        counters.second_count += 1
    elif cell_type == 3:
        counters.third_count += 1


def update_state(state, counters):
    new_state = state.copy()

    for cell in new_state:
        if new_state[cell] != -1:
            neighbors = gu.get_neighbors(cell)

            type1_neighbors = sum(state.get(neighbor, 0) == 1 for neighbor in neighbors)
            type2_neighbors = sum(state.get(neighbor, 0) == 2 for neighbor in neighbors)
            type3_neighbors = sum(state.get(neighbor, 0) == 3 for neighbor in neighbors)
            neighbor_counts = [type1_neighbors, type2_neighbors, type3_neighbors]

            current_state = state[cell]

            if neighbor_counts[0] == neighbor_counts[1] == neighbor_counts[2]:
                new_state[cell] = 0

            if (neighbor_counts[0] > neighbor_counts[2]) and (neighbor_counts[0] in typeparams[0]):
                new_state[cell] = 1

            if (neighbor_counts[1] > neighbor_counts[0]) and (neighbor_counts[1] in typeparams[1]):
                new_state[cell] = 2

            if (neighbor_counts[2] > neighbor_counts[1]) and (neighbor_counts[2] in typeparams[2]):
                new_state[cell] = 3

            if current_state in [1, 2, 3] and survival:
                if neighbor_counts[current_state - 1] in typeparams[current_state - 1]:
                    new_state[cell] = current_state
                else:
                    new_state[cell] = 0

            update_counters(counters, new_state[cell])

    state.clear()
    state.update(new_state)


def precompute_edges(grid_radius):
    edges = set()
    grid_range = [-grid_radius, grid_radius]
    for q in range(-grid_radius, grid_radius + 1):
        for r in range(-grid_radius, grid_radius + 1):
            if q in grid_range or r in grid_range or -q - r in grid_range:
                edges.add((q, r))
    return edges


def clear_edges(state, edges):
    for cell in edges:
        if cell in state:
            state[cell] = 0


def borderline_cells(grid, state):
    borderline = []
    for cell in grid:
        neighbors = gu.get_neighbors(cell)

        neighbor_types = {state.get(neighbor, 0) for neighbor in neighbors if state.get(neighbor, 0) != 0}
        if len(neighbor_types) >= 2:
            borderline.append(cell)

    return borderline


def update_borderline_color(grid, state, BC, screen, CELL_RADIUS, WIDTH, HEIGHT):
    BC.cyan_borderline_cells.clear()
    BC.yellow_borderline_cells.clear()
    BC.white_borderline_cells.clear()
    BC.black_borderline_cells.clear()

    borderline = borderline_cells(grid, state)
    for cell in borderline:
        neighbors = gu.get_neighbors(cell)

        type1_neighbors = sum(state.get(neighbor, 0) == 1 for neighbor in neighbors)
        type2_neighbors = sum(state.get(neighbor, 0) == 2 for neighbor in neighbors)
        type3_neighbors = sum(state.get(neighbor, 0) == 3 for neighbor in neighbors)
        dead_neighbors = sum(state.get(neighbor, 0) == 0 for neighbor in neighbors)

        q, r = gu.hex_to_pixel(CELL_RADIUS, WIDTH, HEIGHT, *cell)

        neighbor_counts = [type1_neighbors, type2_neighbors, type3_neighbors, dead_neighbors]
        max_type_count = max(neighbor_counts)
        all_max_types = [count for count in neighbor_counts if count == max_type_count]
        if len(all_max_types) > 1:
            BC.black_borderline_cells.append(cell)
            gu.draw_hexagon(CELL_RADIUS, screen, gu.Grid_Colors.BLACK, (q, r))
        elif type1_neighbors == max_type_count:
            BC.yellow_borderline_cells.append(cell)
            gu.draw_hexagon(CELL_RADIUS, screen, gu.Grid_Colors.CYAN, (q, r))
        elif type2_neighbors == max_type_count:
            BC.cyan_borderline_cells.append(cell)
            gu.draw_hexagon(CELL_RADIUS, screen, gu.Grid_Colors.YELLOW, (q, r))
        elif type3_neighbors == max_type_count:
            BC.white_borderline_cells.append(cell)
            gu.draw_hexagon(CELL_RADIUS, screen, gu.Grid_Colors.WHITE, (q, r))
        else:
            BC.black_borderline_cells.append(cell)
            gu.draw_hexagon(CELL_RADIUS, screen, gu.Grid_Colors.BLACK, (q, r))


def check_for_death(state):
    counts = [sum(state.get(cell, 0) == t for cell in state) for t in [1, 2, 3]]
    dead_types = counts.count(0)
    return dead_types >= 2


def state_neighborhood(state, cell):
    neighborhood = gu.get_neighbors(cell)
    for neighbor in neighborhood:
        state[neighbor] = state[cell]
