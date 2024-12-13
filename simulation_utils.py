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

            neighborhood = type1_neighbors * type2_neighbors * type3_neighbors

            current_state = state[cell]

            neighbor_counts = [type1_neighbors, type2_neighbors, type3_neighbors]
            max_count = max(neighbor_counts)
            max_types = [i + 1 for i, count in enumerate(neighbor_counts) if count == max_count]

            if len(max_types) > 1:
                max_type = current_state
            else:
                max_type = max_types[0]

            # If neighborhood includes all types, the inactive changes its type to match the most common one.
            if current_state == 0 and neighborhood != 0:
                new_state[cell] = max_type
            # If neighborhood includes at least two types, the inactive changes its type to match the most common one.
            elif current_state == 0 and neighborhood == 0 and max_count in (2, 3):
                new_state[cell] = max_type
                update_counters(counters, max_type)

            if current_state == 2 and type1_neighbors >= 2:
                new_state[cell] = 1
                update_counters(counters, 1)
            elif current_state == 3 and type2_neighbors >= 2:
                new_state[cell] = 2
                update_counters(counters, 2)
            elif current_state == 1 and type3_neighbors >= 2:
                new_state[cell] = 3
                update_counters(counters, 3)

            # Survival of an active cell depends on the number of neighbors of the same type as the cell itself
            if current_state in [1, 2, 3]:
                if neighbor_counts[current_state - 1] in [2, 3]:
                    new_state[cell] = current_state
                    update_counters(counters, current_state)
                else:
                    new_state[cell] = 0
                    update_counters(counters, current_state)

    state.clear()
    state.update(new_state)


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
