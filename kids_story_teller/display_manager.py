import pygame
import pygame_gui
import numpy as np
from constants import BACK_COLOR, REC_COLOR, TEXT_COLOR, REC_SIZE, FONT_SIZE, WIDTH, HEIGHT, KWIDTH, KHEIGHT, MAX_TEXT_LEN_DISPLAY
import textwrap

class DisplayManager:
    """
    Handles display and drawing operations using Pygame and pygame_gui.
    """
    def __init__(self, width=800, height=600):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        # Initialize pygame_gui UI manager.
        self.ui_manager = pygame_gui.UIManager((width, height))
        # Placeholders for slider UI elements.
        self.left_slider = None
        self.right_slider = None
        # Placeholders for image lists and selected indices.
        self.left_images = []
        self.right_images = []
        self.left_index = 0
        self.right_index = 0

    def set_icon(self, icon_path: str):
        """
        Set the window icon and caption.
        """
        icon = pygame.image.load(icon_path)
        pygame.display.set_icon(icon)
        pygame.display.set_caption("Kids Story Teller")

    def create_image_sliders(self, left_images, right_images):
        """
        Creates two horizontal slider components using pygame_gui for selecting images.
        
        Parameters:
            left_images: List of pygame.Surface objects for the left slider.
            right_images: List of pygame.Surface objects for the right slider.
        """
        self.left_images = left_images
        self.right_images = right_images
        screen_width, _ = self.screen.get_size()
        slider_width = screen_width // 2 - 20
        slider_height = 50
        
        # Create the left slider. Its value will represent the index into left_images.
        if left_images:
            self.left_slider = pygame_gui.elements.UIHorizontalSlider(
                relative_rect=pygame.Rect((10, 10), (slider_width, slider_height)),
                start_value=0,
                value_range=(0, len(left_images) - 1),
                manager=self.ui_manager,
                object_id='#left_slider'
            )
        # Create the right slider similarly.
        if right_images:
            self.right_slider = pygame_gui.elements.UIHorizontalSlider(
                relative_rect=pygame.Rect((screen_width // 2 + 10, 10), (slider_width, slider_height)),
                start_value=0,
                value_range=(0, len(right_images) - 1),
                manager=self.ui_manager,
                object_id='#right_slider'
            )

    def process_ui_event(self, event):
        """
        Processes pygame events for the UI elements and updates image selection indices.
        """
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_object_id == '#left_slider':
                # Update left image index (rounding the slider value).
                self.left_index = int(event.value)
            elif event.ui_object_id == '#right_slider':
                self.right_index = int(event.value)
        self.ui_manager.process_events(event)

    def update_ui(self, time_delta):
        """
        Updates UI elements from pygame_gui.
        """
        self.ui_manager.update(time_delta)

    def draw_ui(self):
        """
        Draws the UI elements (sliders) and displays the currently selected images below them.
        """
        # Let pygame_gui draw its UI.
        self.ui_manager.draw_ui(self.screen)
        screen_width, _ = self.screen.get_size()
        
        # Define display areas for the selected images (below sliders).
        left_image_area = pygame.Rect(10, 70, screen_width // 2 - 20, 100)
        right_image_area = pygame.Rect(screen_width // 2 + 10, 70, screen_width // 2 - 20, 100)
        
        # Draw the left selected image.
        if self.left_images and 0 <= self.left_index < len(self.left_images):
            img = self.left_images[self.left_index]
            img_scaled = pygame.transform.scale(img, (left_image_area.width, left_image_area.height))
            self.screen.blit(img_scaled, left_image_area.topleft)
            
        # Draw the right selected image.
        if self.right_images and 0 <= self.right_index < len(self.right_images):
            img = self.right_images[self.right_index]
            img_scaled = pygame.transform.scale(img, (right_image_area.width, right_image_area.height))
            self.screen.blit(img_scaled, right_image_area.topleft)
        
        pygame.display.update()

    def display_message(self, message, color=(0, 0, 0)):
        """
        Clears the screen with a white background and displays a text message
        at the bottom-center with automatic line wrapping.
        """
        self.screen.fill((255, 255, 255))
        max_chars_per_line = 50
        wrapped_lines = []
        for line in message.splitlines():
            wrapped_lines.extend(textwrap.wrap(line, width=max_chars_per_line))
        
        screen_width, screen_height = self.screen.get_size()
        line_height = self.font.get_linesize()
        total_text_height = len(wrapped_lines) * line_height
        bottom_margin = 20
        y_start = screen_height - total_text_height - bottom_margin
        
        for idx, line in enumerate(wrapped_lines):
            text_surface = self.font.render(line, True, color)
            x_position = (screen_width - text_surface.get_width()) / 2
            y_position = y_start + idx * line_height
            self.screen.blit(text_surface, (x_position, y_position))
        
        pygame.display.flip()

    def display_sound_energy(self, energy: float):
        """
        Clears the screen with a white background and visualizes the sound energy using
        a complex, glowing radial effect. The effect consists of multiple concentric circles
        whose sizes and opacities are based on the energy value. The visualization is centered
        at the bottom of the screen.
        
        Parameters:
            energy: A float in [0.0, 1.0] representing the current sound energy.
        """
        # White background.
        self.screen.fill((255, 255, 255))
        screen_width, screen_height = self.screen.get_size()
        bottom_margin = 20

        # Define base and maximum radius.
        min_radius = 20
        max_radius = 150
        energy = min(max(energy, 0.0), 1.0)
        # Interpolate the radius.
        radius = int(min_radius + (max_radius - min_radius) * energy)

        # Center the circle at the bottom-center.
        x_center = screen_width // 2
        y_center = screen_height - bottom_margin - radius

        # Compute a base color that changes with energy.
        base_color = (
            int(255 * energy),            # Red increases with energy.
            int(255 * (1 - energy)),        # Green decreases with energy.
            100                           # Constant blue component.
        )

        # Draw multiple concentric circles for a glowing effect.
        num_rings = 8
        ring_spacing = 6
        for i in range(num_rings):
            ring_radius = radius + i * ring_spacing
            alpha = max(0, 255 - i * 40)
            temp_surface_size = ring_radius * 2 + 2
            temp_surface = pygame.Surface((temp_surface_size, temp_surface_size), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, base_color + (alpha,), (ring_radius, ring_radius), ring_radius)
            self.screen.blit(temp_surface, (x_center - ring_radius, y_center - ring_radius))

        pygame.draw.circle(self.screen, (0, 0, 0), (x_center, y_center), radius, 2)
        pygame.display.flip()

    def tick(self, fps=60):
        """
        Maintains the loop's frame rate.
        """
        self.clock.tick(fps) 