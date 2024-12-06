from dataclasses import dataclass
import math as m
import pygame


@dataclass
class Grid_Colors:
    COLOR_D = 40
    WHITE = (255, 255, 255)
    GRAY = (200, 200, 200)
    DARK_GRAY = (100, 100, 100)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    CYAN = (0, 255, 255)


def generate_hex_grid(radius):
    grid = []
    for q in range(-radius, radius + 1):
        for r in range(-radius, radius + 1):
            if abs(q + r) <= radius:
                grid.append((q, r))
    return grid


def hex_to_pixel(CELL_RADIUS, WIDTH, HEIGHT, q, r):
    x = CELL_RADIUS * (3 / 2 * q)
    y = CELL_RADIUS * (m.sqrt(3) * (r + q / 2))
    return int(x + WIDTH // 2), int(y + HEIGHT // 2)


def draw_hexagon(CELL_RADIUS, surface, color, pos):
    x, y = pos
    points = []
    for i in range(6):
        angle = m.pi / 3 * i
        point_x = x + CELL_RADIUS * m.cos(angle)
        point_y = y + CELL_RADIUS * m.sin(angle)
        points.append((point_x, point_y))
    pygame.draw.polygon(surface, color, points)
    # pygame.draw.polygon(surface, GRAY, points, 1)


def get_neighbors(cell):
    q, r = cell
    directions = [
        (1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)
    ]
    return [(q + dq, r + dr) for dq, dr in directions]
