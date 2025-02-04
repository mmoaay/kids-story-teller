import pygame
import pygame.locals
import numpy as np
from constants import BACK_COLOR, REC_COLOR, TEXT_COLOR, REC_SIZE, FONT_SIZE, WIDTH, HEIGHT, KWIDTH, KHEIGHT, MAX_TEXT_LEN_DISPLAY

class DisplayManager:
    """
    Handles display and drawing operations using Pygame.
    """
    def __init__(self):
        # Initialize the Pygame display surface and clock.
        self.window_surface = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
        self.font = pygame.font.SysFont(None, FONT_SIZE)
        self.clock = pygame.time.Clock()

    def set_icon(self, icon_path: str):
        """
        Set the window icon and caption.
        """
        icon_image = pygame.image.load(icon_path)
        pygame.display.set_icon(icon_image)
        pygame.display.set_caption("Assistant")

    def display_message(self, text: str):
        """
        Render and display a text message at the center of the screen.
        """
        self.window_surface.fill(BACK_COLOR)
        display_text = text if len(text) < MAX_TEXT_LEN_DISPLAY else text[0:MAX_TEXT_LEN_DISPLAY] + "..."
        label = self.font.render(display_text, True, TEXT_COLOR)
        label_rect = label.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.window_surface.blit(label, label_rect)
        pygame.display.flip()

    def display_rec_start(self):
        """
        Display a red circle to indicate the start of recording.
        """
        self.window_surface.fill(BACK_COLOR)
        pygame.draw.circle(self.window_surface, REC_COLOR, (WIDTH // 2, HEIGHT // 2), REC_SIZE)
        pygame.display.flip()

    def display_sound_energy(self, energy: float):
        """
        Visualize sound energy on the screen.
        """
        col_count = 5
        red_center = 150
        factor = 10
        max_amplitude = 100

        self.window_surface.fill(BACK_COLOR)
        amplitude = int(max_amplitude * energy)
        hspace = 2 * KWIDTH
        vspace = int(KHEIGHT / 2)

        def rect_coords(x, y):
            return (int(x - KWIDTH / 2), int(y - KHEIGHT / 2), KWIDTH, KHEIGHT)

        center_x = WIDTH / 2
        center_y = HEIGHT / 2
        for idx in range(-int(np.floor(col_count / 2)), int(np.ceil(col_count / 2))):
            x = center_x + (idx * hspace)
            y = center_y
            count = amplitude - 2 * abs(idx)
            mid = int(np.ceil(count / 2))
            for i in range(mid):
                color = (red_center + (factor * (i % mid)), 0, 0)
                offset = i * (KHEIGHT + vspace)
                pygame.draw.rect(self.window_surface, color, rect_coords(x, y + offset))
                # Draw a mirrored rectangle on the opposite side.
                pygame.draw.rect(self.window_surface, color, rect_coords(x, y - offset))
        pygame.display.flip() 