import pygame
from pygame.surface import Surface
from pygame.rect import Rect


class SpriteFromSheet:
    def __init__(
        self, x: int, y: int, width: int, height: int, scale: float, sheet: str
    ) -> None:
        sprite: Surface = pygame.Surface(
            (width, height), pygame.SRCALPHA
        ).convert_alpha()

        sprite.blit(pygame.image.load(sheet), (0, 0), (x, y, width, height))
        sprite = pygame.transform.scale(sprite, (width * scale, height * scale))

        self.sprite: Surface = sprite
        self.rect: Rect = sprite.get_rect()

    def draw(self, surface: Surface) -> None:
        surface.blit(self.sprite, self.rect)
