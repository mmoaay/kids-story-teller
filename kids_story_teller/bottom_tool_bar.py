import pygame
import textwrap
import pygame_gui

# Global debug flag for draw methods.
DEBUG_DRAW = True

# Custom circular button class based on pygame_gui's UIButton.
class UICircularButton(pygame_gui.elements.UIButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 清空主题生成的 image ，确保后续使用我们的方式来重建形象
        self.image = None

    def update(self, time_delta):
        # 先调用父类更新状态等逻辑
        super().update(time_delta)
        
        # 根据当前状态重新生成圆形按钮的 image
        button_rect = self.relative_rect
        circular_surface = pygame.Surface(
            (button_rect.width, button_rect.height), pygame.SRCALPHA
        )
        
        # 判断鼠标左键是否按下
        # 注意：pygame.mouse.get_pressed()[0] 表示左键是否按下
        if self.hovered and pygame.mouse.get_pressed()[0]:
            color = (231, 151, 150)  # 按下状态颜色
        elif self.hovered:
            color = (255, 178, 132)  # 悬停状态颜色
        else:
            color = (255, 201, 136)  # 普通状态颜色

        # 更新按钮的图像，用于后续 UIManager 的 draw_ui 调用
        self.image = circular_surface
        
        # 绘制圆形背景
        pygame.draw.circle(
            circular_surface, color, (button_rect.width // 2, button_rect.height // 2), button_rect.width // 2
        )
        

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

        # Save layout constants for later use.
        self.pad = pad
        self.button_size = button_size

        # Define the toolbar area.
        self.rect = pygame.Rect(0, screen_height - toolbar_height, screen_width, toolbar_height)

        # Create a UI Manager for the toolbar area.
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

        # Define the center message area that stretches between the two buttons.
        message_x = self.left_button.relative_rect.right
        message_width = self.right_button.relative_rect.left - message_x
        self.message_rect = pygame.Rect(message_x, pad, message_width, toolbar_height - 2 * pad)
        self.message = ""
        self.font = pygame.font.Font(None, 24)

    def set_message(self, message: str):
        self.message = message

    def process_events(self, event):
        # Let the pygame_gui manager process events.
        self.ui_manager.process_events(event)

    def draw(self, surface, energy: float):
        # 创建工具栏专用的 surface，背景颜色为 #B0BEAF (RGB: 176, 190, 175)
        toolbar_surface = pygame.Surface((self.width, self.height))
        toolbar_surface.fill((209, 220, 226))
    
        # 更新并绘制 UI 按钮。
        time_delta = 1.0 / 60.0
        self.ui_manager.update(time_delta)
        self.ui_manager.draw_ui(toolbar_surface)
    
        # 渲染并显示中间的消息文本。
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