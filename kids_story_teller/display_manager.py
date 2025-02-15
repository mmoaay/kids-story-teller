import pygame
import numpy as np
from constants import BACK_COLOR, REC_COLOR, TEXT_COLOR, REC_SIZE, FONT_SIZE, WIDTH, HEIGHT, KWIDTH, KHEIGHT, MAX_TEXT_LEN_DISPLAY
import textwrap

class SoundEnergyControl:
    """
    Independent sound energy component, displayed as a 100x100 pixel surface.
    It uses multiple concentric circles to create a glowing effect that varies with the energy value.
    A green border is drawn around the widget, and a microphone-shaped icon is displayed in the center.
    """
    def __init__(self, size=100):
        self.size = size
        self.surface = pygame.Surface((size, size), pygame.SRCALPHA)
        # Attempt to load the microphone icon from the resources folder.
        try:
            self.mic_icon = pygame.image.load("resources/mic_icon.png").convert_alpha()
            # Optionally scale the icon to a suitable size (e.g., 50x50)
            self.mic_icon = pygame.transform.smoothscale(self.mic_icon, (50, 50))
        except Exception as e:
            print(f"Failed to load microphone icon: {e}")
            self.mic_icon = None

    def render(self, energy: float):
        size = self.size
        # Clear previous drawing (using a transparent background)
        self.surface.fill((255, 255, 255, 0))
        
        # Define parameters for a size display
        min_radius = 10
        max_radius = 40
        energy = min(max(energy, 0.0), 1.0)
        radius = int(min_radius + (max_radius - min_radius) * energy)
        x_center = size // 2
        y_center = size // 2
        base_color = (int(255 * energy), int(255 * (1 - energy)), 100)
        
        num_rings = 4
        ring_spacing = 3
        for i in range(num_rings):
            ring_radius = radius + i * ring_spacing
            alpha = max(0, 255 - i * 60)
            temp_surface_size = ring_radius * 2 + 2
            temp_surface = pygame.Surface((temp_surface_size, temp_surface_size), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, base_color + (alpha,), (ring_radius, ring_radius), ring_radius)
            pos = (x_center - ring_radius, y_center - ring_radius)
            self.surface.blit(temp_surface, pos)
        
        # Removed drawing of the inner black circle border
        
        # Add a green border around the entire component
        border_thickness = 3
        border_radius = size // 2 - 2  # Adjusting for a small margin
        pygame.draw.circle(self.surface, (0, 255, 0), (x_center, y_center), border_radius, border_thickness)
        
        # Draw a microphone icon in the center, if available
        if self.mic_icon:
            mic_rect = self.mic_icon.get_rect(center=(x_center, y_center))
            self.surface.blit(self.mic_icon, mic_rect)
        
        return self.surface

class BottomToolBar:
    """
    Bottom toolbar component with a fixed height of 100 pixels, which contains:
      - A 80x80 green circular button on the left with 10 pixels padding on all sides.
      - A center message text area that is vertically centered and touches the left and right buttons.
      - The sound energy component on the right, sized 80x80 with 10 pixels padding.
    """
    def __init__(self, screen_width, screen_height, toolbar_height=100):
        pad = 10
        button_size = 80
        
        self.toolbar_height = toolbar_height
        self.width = screen_width
        self.height = toolbar_height
        
        # Define the toolbar area (located at the bottom of the screen)
        self.rect = pygame.Rect(0, screen_height - toolbar_height, screen_width, toolbar_height)
        
        # Left green button rectangle with a padding of 10
        self.button_rect = pygame.Rect(pad, pad, button_size, button_size)
        self.button_color = (0, 255, 0)
        
        # Right sound energy control rectangle with the same dimensions and padding
        self.sound_energy_control = SoundEnergyControl(size=button_size)
        self.sound_energy_rect = pygame.Rect(screen_width - pad - button_size, pad, button_size, button_size)
        
        # Center message text area touches the buttons horizontally (no extra margin)
        message_x = self.button_rect.right
        message_width = self.sound_energy_rect.left - self.button_rect.right
        # Vertical space: from pad to toolbar_height-pad gives a height of toolbar_height-2*pad (i.e. 80)
        self.message_rect = pygame.Rect(message_x, pad, message_width, toolbar_height - 2 * pad)
        
        self.message = ""
        self.font = pygame.font.Font(None, 24)
        
        # Callback for the left green button (can be set externally)
        self.button_callback = None

    def set_message(self, message: str):
        self.message = message

    def set_button_callback(self, callback):
        self.button_callback = callback

    def handle_event(self, event):
        # Check for a mouse button down event on the left green button.
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                # Convert from global to toolbar-local coordinates
                local_pos = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
                if self.button_rect.collidepoint(local_pos):
                    if self.button_callback:
                        self.button_callback()

    def draw(self, surface, energy: float):
        # Create a dedicated surface for the toolbar with a light gray background.
        toolbar_surface = pygame.Surface((self.width, self.height))
        toolbar_surface.fill((211, 211, 211))  # Light gray background

        # Draw the left green button (using ellipse for a circular look)
        pygame.draw.ellipse(toolbar_surface, self.button_color, self.button_rect)

        # Draw the right sound energy component
        sound_surface = self.sound_energy_control.render(energy)
        toolbar_surface.blit(sound_surface, self.sound_energy_rect.topleft)

        # Render and vertically center the message text in the center message area.
        if self.message:
            max_chars = 20
            lines = []
            for line in self.message.splitlines():
                lines.extend(textwrap.wrap(line, width=max_chars))
            
            # Calculate total height of all rendered lines
            total_height = 0
            text_surfaces = []
            for line in lines:
                tsurf = self.font.render(line, True, (0, 0, 0))
                text_surfaces.append(tsurf)
                total_height += tsurf.get_height()
            
            # Start-Y is determined to vertically center the block of text within message_rect.
            start_y = self.message_rect.top + (self.message_rect.height - total_height) / 2
            for tsurf in text_surfaces:
                text_rect = tsurf.get_rect(centerx=self.message_rect.centerx, y=start_y)
                toolbar_surface.blit(tsurf, text_rect)
                start_y += tsurf.get_height()

        # Blit the complete toolbar surface onto the main screen at its designated area.
        surface.blit(toolbar_surface, self.rect.topleft)

class DisplayManager:
    """
    Manages the entire Pygame display rendering and divides the screen into two sections:
      - Top: Displays the top_image, which fills the space above the bottom toolbar.
      - Bottom: The bottom toolbar (100 pixels high) containing the left green button, centered message text, and the right sound energy display.
    """
    def __init__(self, width=800, height=600):
        # Assume pygame.init() is called already in the main module.
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Kids Story Teller")  # Set window caption for clarity
        self.clock = pygame.time.Clock()
        self.bg_color = (255, 255, 255)  # White background
        
        # Initialize the bottom toolbar
        self.bottom_toolbar = BottomToolBar(width, height, toolbar_height=100)
        self.bottom_toolbar.set_button_callback(self.on_green_button_click)
        
        self.top_image = None  # Holds the image for the top portion of the screen.
        self.current_energy = 0.0  # Sound energy value for the sound energy control.

    def set_icon(self, icon_path: str):
        """
        Set the window icon by loading the image from the provided file name in the resources folder.
        """
        try:
            icon_surface = pygame.image.load("resources/" + icon_path)
            pygame.display.set_icon(icon_surface)
        except Exception as e:
            print(f"Failed to set icon: {e}")

    def on_green_button_click(self):
        # Event handler for left green button click.
        print("Green button clicked!")
        # Additional logic can be added here.

    def set_top_image(self, image):
        """
        Set the top image displayed in the area above the bottom toolbar.
        Parameter:
            image: pygame.Surface object or a string representing the file name in the resources folder.
        """
        if isinstance(image, str):
            try:
                self.top_image = pygame.image.load("resources/" + image).convert_alpha()
            except Exception as e:
                print(f"Failed to load top image from 'resources/{image}': {e}")
                self.top_image = None
        else:
            self.top_image = image

    def set_message(self, message: str):
        """
        Update the center message of the bottom toolbar.
        """
        self.bottom_toolbar.set_message(message)

    def set_energy(self, energy: float):
        """
        Update the sound energy value dynamically shown on the sound energy control.
        """
        self.current_energy = energy

    def handle_event(self, event):
        # Delegate event handling to the bottom toolbar.
        self.bottom_toolbar.handle_event(event)
        # Additional global events can be processed here.

    def draw(self):
        # Fill the entire screen background.
        self.screen.fill(self.bg_color)
        
        # Define the top area height (space above the bottom toolbar)
        top_area_height = self.screen.get_height() - 100
        if self.top_image:
            available_width = self.screen.get_width()
            available_height = top_area_height
            
            # Compute scaling to preserve aspect ratio.
            orig_width, orig_height = self.top_image.get_size()
            scale_factor = min(available_width / orig_width, available_height / orig_height)
            new_width = int(orig_width * scale_factor)
            new_height = int(orig_height * scale_factor)
            
            # Smoothly scale and center the top image.
            top_image_scaled = pygame.transform.smoothscale(self.top_image, (new_width, new_height))
            top_area_rect = pygame.Rect(0, 0, available_width, available_height)
            top_image_rect = top_image_scaled.get_rect(center=top_area_rect.center)
            self.screen.blit(top_image_scaled, top_image_rect.topleft)
        else:
            pygame.draw.rect(self.screen, self.bg_color, pygame.Rect(0, 0, self.screen.get_width(), top_area_height))
        
        # Draw the bottom toolbar.
        self.bottom_toolbar.draw(self.screen, self.current_energy)
        
        pygame.event.pump()
        pygame.display.update()

    def tick(self, fps=60):
        self.clock.tick(fps)