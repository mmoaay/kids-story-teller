import pygame
import textwrap
import pygame_gui

# Global debug flag for draw methods.
DEBUG_DRAW = True

# Custom circular button class based on pygame_gui's UIButton.
class UICircularButton(pygame_gui.elements.UIButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Clear the theme-generated image to ensure our custom rendering.
        self.image = None

    def update(self, time_delta):
        # Call the superclass update to process logic.
        super().update(time_delta)
        
        # Recreate the button's image based on its current state.
        button_rect = self.relative_rect
        circular_surface = pygame.Surface(
            (button_rect.width, button_rect.height), pygame.SRCALPHA
        )
        
        # Determine the button state based on mouse hover and left-button press.
        if self.hovered and pygame.mouse.get_pressed()[0]:
            color = (231, 151, 150)  # Color for pressed state.
        elif self.hovered:
            color = (255, 178, 132)  # Color for hover state.
        else:
            color = (255, 201, 136)  # Color for normal state.

        # Draw circular background.
        pygame.draw.circle(
            circular_surface,
            color,
            (button_rect.width // 2, button_rect.height // 2),
            button_rect.width // 2,
        )
        
        # Update the button's image for UIManager's draw_ui call.
        self.image = circular_surface

class BottomToolBar:
    """
    Bottom toolbar component that occupies a fixed height at the bottom of the screen.
    This implementation uses pygame_gui to provide two circular UI buttons on the left and right.
    The center area displays a message that is rendered manually.
    """
    def __init__(self, screen_width, screen_height, toolbar_height=100):
        pad = 10
        button_size = 80

        self.toolbar_height = toolbar_height
        self.width = screen_width
        self.height = toolbar_height

        # Store layout constants for later use.
        self.pad = pad
        self.button_size = button_size

        # Define the toolbar area.
        self.rect = pygame.Rect(0, screen_height - toolbar_height, screen_width, toolbar_height)

        # Create a UIManager for the toolbar area.
        self.ui_manager = pygame_gui.UIManager((self.width, self.height))

        # Create left and right circular buttons using the custom UICircularButton.
        self.left_button = UICircularButton(
            relative_rect=pygame.Rect(pad, pad, button_size, button_size),
            text='Left',
            manager=self.ui_manager
        )
        self.right_button = UICircularButton(
            relative_rect=pygame.Rect(self.width - pad - button_size, pad, button_size, button_size),
            text='Right',
            manager=self.ui_manager
        )

        # Define the center message area stretching between the two buttons.
        message_x = self.left_button.relative_rect.right
        message_width = self.right_button.relative_rect.left - message_x
        self.message_rect = pygame.Rect(message_x, pad, message_width, toolbar_height - 2 * pad)
        self.message = ""
        self.font = pygame.font.Font(None, 24)

    def set_message(self, message: str):
        self.message = message

    def process_events(self, event):
        # Delegate event processing to the pygame_gui manager.
        self.ui_manager.process_events(event)

    def draw(self, surface, energy: float):
        # Create a dedicated toolbar surface with background color (209, 220, 226).
        toolbar_surface = pygame.Surface((self.width, self.height))
        toolbar_surface.fill((209, 220, 226))
    
        # Update and render UI buttons.
        time_delta = 1.0 / 60.0
        self.ui_manager.update(time_delta)
        self.ui_manager.draw_ui(toolbar_surface)
    
        # Render and display the center message text.
        if self.message:
            max_chars = 20
            lines = []
            for line in self.message.splitlines():
                lines.extend(textwrap.wrap(line, width=max_chars))
            total_height = 0
            text_surfaces = []
            for line in lines:
                tsurf = self.font.render(line, True, (0, 0, 0))
                text_surfaces.append(tsurf)
                total_height += tsurf.get_height()
            start_y = self.message_rect.top + (self.message_rect.height - total_height) / 2
            for tsurf in text_surfaces:
                text_rect = tsurf.get_rect(centerx=self.message_rect.centerx, y=start_y)
                toolbar_surface.blit(tsurf, text_rect)
                start_y += tsurf.get_height()
    
        surface.blit(toolbar_surface, self.rect.topleft) 