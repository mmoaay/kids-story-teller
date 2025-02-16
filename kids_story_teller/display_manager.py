import pygame
import pygame_gui
import textwrap
from bottom_tool_bar import BottomToolBar
# If needed elsewhere, you can import SoundEnergyControl as follows:
# from sound_energy_control import SoundEnergyControl

class DisplayManager:
    """
    Manages the entire Pygame display rendering and divides the screen into two sections:
      - Top: Displays the top_image, which fills the space above the bottom toolbar.
      - Bottom: The toolbar containing two buttons (left and right) and a center message.
    """
    def __init__(self, width=800, height=600):
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Kids Story Teller")
        self.clock = pygame.time.Clock()
        self.bg_color = (255, 255, 255)  # White background

        # Initialize the bottom toolbar.
        self.bottom_toolbar = BottomToolBar(width, height, toolbar_height=100)
        # Example callback assignment (set externally as needed)
        self.bottom_toolbar.left_button_callback = lambda: print("Left button clicked!")
        self.bottom_toolbar.right_button_press_callback = lambda: print("Right button pressed!")
        self.bottom_toolbar.right_button_release_callback = lambda: print("Right button released!")

        self.top_image = None
        self.current_energy = 0.0

    def set_icon(self, icon_path: str):
        try:
            icon_surface = pygame.image.load("resources/" + icon_path)
            pygame.display.set_icon(icon_surface)
        except Exception as e:
            print(f"Failed to set icon: {e}")

    def set_top_image(self, image):
        if isinstance(image, str):
            try:
                self.top_image = pygame.image.load("resources/" + image).convert_alpha()
            except Exception as e:
                print(f"Failed to load top image from 'resources/{image}': {e}")
                self.top_image = None
        else:
            self.top_image = image

    def set_message(self, message: str):
        self.bottom_toolbar.set_message(message)

    def set_energy(self, energy: float):
        self.current_energy = energy

    def process_events(self, event):
        # Delegate UI events to the bottom toolbar.
        self.bottom_toolbar.process_events(event)

    def draw(self):
        self.screen.fill(self.bg_color)
        top_area_height = self.screen.get_height() - 100
        if self.top_image:
            available_width = self.screen.get_width()
            available_height = top_area_height

            orig_width, orig_height = self.top_image.get_size()
            scale_factor = min(available_width / orig_width, available_height / orig_height)
            new_width = int(orig_width * scale_factor)
            new_height = int(orig_height * scale_factor)
            
            top_image_scaled = pygame.transform.smoothscale(self.top_image, (new_width, new_height))
            top_area_rect = pygame.Rect(0, 0, available_width, available_height)
            top_image_rect = top_image_scaled.get_rect(center=top_area_rect.center)
            self.screen.blit(top_image_scaled, top_image_rect.topleft)
        else:
            pygame.draw.rect(self.screen, self.bg_color, pygame.Rect(0, 0, self.screen.get_width(), top_area_height))
        
        self.bottom_toolbar.draw(self.screen, self.current_energy)

        pygame.display.update()