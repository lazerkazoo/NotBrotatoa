import json
import math

import pygame
from scripts.bullet import Bullet

with open("data/gun_types.json", "r") as f:
    gun_types = json.load(f)
    f.close()


class Gun:
    def __init__(self, type: str) -> None:
        self.type = type

        self.data = gun_types[type]
        self.damage = self.data["damage"]
        self.rate = self.data["rate"]
        self.spread = self.data["spread"]

        self.bullet_data = self.data["bullet"]
        self.size = self.bullet_data["size"]
        self.speed = self.bullet_data["speed"]
        self.lifetime = self.bullet_data["lifetime"]
        self.pierce = self.bullet_data["pierce"]

        self.bullets: list[Bullet] = []

        self.rect = pygame.rect.Rect((0, 0), (self.size, self.size))

    def shoot(self, target: tuple[int, int], start_pos: tuple[int, int]) -> None:
        dx = target[0] - start_pos[0]
        dy = target[1] - start_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)

        if distance <= 0:
            return

        base_direction = [dx / distance, dy / distance]

        num_bullets = max(1, int(self.spread))

        for i in range(num_bullets):
            if num_bullets == 1:
                angle_offset = 0
            else:
                spread_angle = math.pi / 6
                angle_offset = (
                    (i - (num_bullets - 1) / 2)
                    * spread_angle
                    / max(1, (num_bullets - 1))
                )

            cos_angle = math.cos(angle_offset)
            sin_angle = math.sin(angle_offset)
            direction_x = base_direction[0] * cos_angle - base_direction[1] * sin_angle
            direction_y = base_direction[0] * sin_angle + base_direction[1] * cos_angle

            bullet = Bullet(
                start_pos,
                target,
                self.damage,
                self.lifetime,
                self.speed,
                self.size,
                self.pierce,
            )
            self.bullets.append(bullet)

    def update(self) -> None:
        self.bullets[:] = [bullet for bullet in self.bullets if not bullet.update()]

    def draw(self, surface: pygame.Surface) -> None:
        for bullet in self.bullets:
            bullet.draw(surface)

    def get_bullets(self) -> list[Bullet]:
        return self.bullets

    def clear_bullets(self) -> None:
        self.bullets.clear()
