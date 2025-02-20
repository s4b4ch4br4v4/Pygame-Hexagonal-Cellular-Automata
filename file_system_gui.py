import pygame
import os


def select_file(directory):
    current_screen = pygame.display.get_surface()
    current_caption = pygame.display.get_caption()
    current_size = current_screen.get_size()

    WIDTH, HEIGHT = 500, 300
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Configuration loading")
    font = pygame.font.SysFont('Arial', 24)

    files = [f for f in os.listdir(directory) if f.endswith(".txt")]

    scroll_y = 0
    scroll_speed = 40
    running = True
    selected_file = None

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)

    def display_files():
        screen.fill(WHITE)
        y_offset = 10 - scroll_y
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for i, file in enumerate(files):
            if 10 + i * 40 - scroll_y < mouse_y < 40 + i * 40 - scroll_y:
                pygame.draw.rect(screen, GRAY, (0, y_offset, WIDTH, 30))
            if 0 <= y_offset <= HEIGHT:
                text_surface = font.render(file, True, BLACK)
                screen.blit(text_surface, (10, y_offset))
            y_offset += 40

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    scroll_y = max(0, scroll_y - scroll_speed)
                elif event.y < 0:
                    scroll_y = min((len(files) - 1) * 40 - HEIGHT, scroll_y + scroll_speed)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button only
                    x, y = event.pos
                    for i, file in enumerate(files):
                        if 10 + i * 40 - scroll_y < y < 40 + i * 40 - scroll_y:
                            selected_file = file
                            running = False
        display_files()
        pygame.display.flip()

    pygame.display.set_mode(current_size)
    pygame.display.set_caption(current_caption[0])
    return os.path.join(directory, selected_file) if selected_file else None
