import pygame


class Text:
    def __init__(
        self, text: str, font_size: int, color: str = "black", bg: str = None
    ) -> None:
        self.text = text
        self.color = pygame.color.Color(color)
        self.bg_color = bg
        self.font = pygame.font.Font("assets/font/editundo.ttf", font_size)
        self.surface = self.font.render(text, False, self.color, bg).convert_alpha()
        self.rect = self.surface.get_rect()

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.surface, self.rect)

    def update_txt(self) -> None:
        self.surface = self.font.render(
            self.text, False, self.color, self.bg_color
        ).convert_alpha()
        self.rect = self.surface.get_rect(center=self.rect.center)

    def check_can_press(self, rect: pygame.Rect) -> bool:
        return self.rect.colliderect(rect)
