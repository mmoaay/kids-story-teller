import pygame

class SoundEnergyControl:
    """
    Independent sound energy component, displayed as a 100x100 pixel surface.
    It uses multiple concentric circles to create a glowing effect that varies with the energy value.
    A green border is drawn around the widget, and a microphone-shaped icon is displayed in the center.
    """
    def __init__(self, size=100):
        self.size = size
        self.surface = pygame.Surface((size, size), pygame.SRCALPHA)
        try:
            self.mic_icon = pygame.image.load("resources/mic_icon.png").convert_alpha()
            self.mic_icon = pygame.transform.smoothscale(self.mic_icon, (50, 50))
        except Exception as e:
            print(f"Failed to load microphone icon: {e}")
            self.mic_icon = None

    def render(self, energy: float):
        size = self.size
        self.surface.fill((255, 255, 255, 0))
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
        
        border_thickness = 3
        border_radius = size // 2 - 2
        pygame.draw.circle(self.surface, (0, 255, 0), (x_center, y_center), border_radius, border_thickness)
        
        if self.mic_icon:
            mic_rect = self.mic_icon.get_rect(center=(x_center, y_center))
            self.surface.blit(self.mic_icon, mic_rect)
        
        return self.surface 