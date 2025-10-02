import json
import math

import pygame


class Bullet:
    def __init__(
        self,
        start_pos: tuple[int, int],
        target_pos: tuple[int, int],
        damage: int,
        lifetime: int,
        speed: int,
        size: int,
        pierce: int,
    ) -> None:
        with open("data/constants.json", "r") as f:
            constants = json.load(f)
            f.close()

        self.FPS = constants["fps"]

        self.start_pos = start_pos
        self.pos = list(start_pos)  # Convert to list for mutability
        self.target = target_pos
        self.speed = speed
        self.size = size
        self.damage = damage
        self.lifetime = lifetime * self.FPS
        self.lifetime_counter = 0
        self.pierce = pierce

        # Calculate direction vector
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            self.direction = [dx / distance * speed, dy / distance * speed]
        else:
            self.direction = [0, 0]  # Target is same as start position

        self.sprite = pygame.Surface((self.size, self.size))
        self.sprite.fill((255, 255, 0))  # Yellow bullet for visibility
        self.rect = self.sprite.get_rect(center=self.pos)

    def update(self) -> bool:
        if self.lifetime_counter >= self.lifetime or self.pierce <= 0:
            return True

        self.lifetime_counter += 1

        # Move bullet in direction
        self.pos[0] += self.direction[0]
        self.pos[1] += self.direction[1]

        self.rect.center = self.pos

        return False  # Bullet should continue

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.sprite, self.rect)

    def get_damage(self) -> int:
        return self.damage

    def get_position(self) -> tuple[float, float]:
        return tuple(self.pos)

    def delete(self) -> None:
        self.lifetime = 0
