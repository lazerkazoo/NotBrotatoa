import pygame
from pygame.rect import Rect
from pygame.surface import Surface


class SpriteFromSheet:
    def __init__(
        self, x: int, y: int, width: int, height: int, scale: float, sheet: str
    ) -> None:
        sprite: Surface = pygame.Surface(
            (width, height), pygame.SRCALPHA
        ).convert_alpha()

        sprite.blit(pygame.image.load(sheet), (0, 0), (x, y, width, height))
        # Use scale_by for pixel-perfect scaling (nearest-neighbor)
        sprite = pygame.transform.scale_by(sprite, scale)

        self.sprite: Surface = sprite
        self.rect: Rect = sprite.get_rect()

    def draw(self, surface: Surface) -> None:
        surface.blit(self.sprite, self.rect)
