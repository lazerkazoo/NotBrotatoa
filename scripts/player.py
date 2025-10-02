import json
from time import sleep
from typing import Callable

import pygame
from pygame.math import Vector2
from pygame import Surface
from pygame.rect import Rect
from scripts.sprite_sheet import SpriteFromSheet


class Player:
    def __init__(self, scale: int, pos: tuple[int, int]) -> None:
        with open("data/constants.json", "r") as f:
            constants = json.load(f)
            f.close()

        self.FPS = constants["fps"]

        self.PLAYER_HEALTH: int = constants["player_health"]
        self.PLAYER_SPEED: int = constants["player_speed"]

        self.width, self.height = constants["width"], constants["height"]

        self.anims = {"Walk": [], "Idle": []}

        self.anim = "Idle"
        self.anim_frame = 0
        self.anim_timer = 12

        self.invinsiblility_time = constants["invinsible_time"]
        self.invinsible_timer = 0

        self.rotation = 1

        self.vel = Vector2(0, 0)
        self.pos: Vector2 = Vector2(pos[0], pos[1])
        self.scale = scale
        self.sprite = SpriteFromSheet(
            0, 0, 32, 32, self.scale, "assets/sprites/player.png"
        )

        self.rect: Rect = self.sprite.sprite.get_rect()
        self.hitbox = pygame.Rect(16 * scale, 16 * scale, 16 * scale, 16 * scale)

        self.load_anims()

        self.health = self.PLAYER_HEALTH
        self.max_health = self.PLAYER_HEALTH * 3

    def load_anims(self) -> None:
        for anim in range(6):
            animation = SpriteFromSheet(
                32 * anim, 32, 32, 32, self.scale, "assets/sprites/player.png"
            )
            self.anims["Walk"].append(animation)

        for anim in range(2):
            animation = SpriteFromSheet(
                32 * anim, 0, 32, 32, self.scale, "assets/sprites/player.png"
            )
            self.anims["Idle"].append(animation)

    def draw(self, surface: Surface) -> None:
        if self.rotation == 0:  # Facing left
            flipped_sprite = pygame.transform.flip(
                self.sprite.sprite, True, False
            ).convert_alpha()
            surface.blit(flipped_sprite, self.rect)
        else:
            surface.blit(self.sprite.sprite, self.rect)

    def update_anim(self):
        self.anim_timer -= 1
        if self.anim_timer <= 0:
            self.anim_timer = 12
            self.anim_frame = (self.anim_frame + 1) % len(self.anims[self.anim])
            if self.anim_frame >= len(self.anims[self.anim]):
                self.anim_frame = 0

            self.sprite = self.anims[self.anim][self.anim_frame]

    def update_pos(self) -> None:
        keys = pygame.key.get_pressed()

        self.anim = "Idle"
        vel_x, vel_y = 0.0, 0.0

        if keys[pygame.K_w]:
            vel_y = -self.PLAYER_SPEED
            self.anim = "Walk"
        if keys[pygame.K_s]:
            vel_y = self.PLAYER_SPEED
            self.anim = "Walk"
        if keys[pygame.K_a]:
            self.rotation = 0
            vel_x = -self.PLAYER_SPEED
            self.anim = "Walk"
        if keys[pygame.K_d]:
            self.rotation = 1
            vel_x = self.PLAYER_SPEED
            self.anim = "Walk"

        self.vel = Vector2(vel_x, vel_y)

        self.pos += self.vel
        self.rect.center = self.pos
        self.hitbox.center = self.pos
        self.hitbox.y += 8 * self.scale

    def take_damage(self, damage: int, todo: Callable[[], None]) -> None:
        if self.invinsible_timer > 0:
            return
        self.health -= damage
        self.invinsible_timer = self.invinsiblility_time * self.FPS
        if self.health <= 0:
            sleep(0.25)
            todo()
            self.health = self.PLAYER_HEALTH
