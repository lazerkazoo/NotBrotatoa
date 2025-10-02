from numpy._core.numerictypes import ScalarType
import pygame
import math
from typing import Optional, Dict, Any, List
from scripts.sprite_sheet import SpriteFromSheet

# Global animation cache to reuse animations across enemies
_ANIMATION_CACHE: Dict[tuple, List[SpriteFromSheet]] = {}


def preload_animations() -> None:
    """Preload all animations to avoid loading them repeatedly"""
    scales = [1, 2, 3, 4]  # Common scales used in the game

    for scale in scales:
        cache_key = ("enemy_walk", scale)
        if cache_key not in _ANIMATION_CACHE:
            _ANIMATION_CACHE[cache_key] = [
                SpriteFromSheet(32 * i, 32, 32, 32, scale, "assets/sprites/player.png")
                for i in range(6)
            ]


def get_enemy_animations(scale: int) -> List[SpriteFromSheet]:
    """Get preloaded animations for the given scale"""
    cache_key = ("enemy_walk", scale)
    if cache_key not in _ANIMATION_CACHE:
        # Fallback: create animations if not preloaded
        _ANIMATION_CACHE[cache_key] = [
            SpriteFromSheet(32 * i, 32, 32, 32, scale, "assets/sprites/player.png")
            for i in range(6)
        ]
    return _ANIMATION_CACHE[cache_key]


class Enemy:
    def __init__(
        self,
        scale: int,
        pos: tuple[int, int],
        enemy_type: str = "normal",
        enemy_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.scale = scale
        self.pos = list(pos)  # Convert to list for easier modification
        self.enemy_type = enemy_type

        # Set enemy properties from data or defaults
        data = enemy_data[enemy_type]
        self.speed = data.get("speed")
        self.health = data.get("health")
        self.damage = data.get("damage")
        self.points = data.get("points")

        self.max_health = self.health
        self.target: Optional[pygame.Rect] = None

        self.anims: List[SpriteFromSheet] = get_enemy_animations(self.scale)
        self.anim_frame = 0
        self.anim_timer = max(1, int(12 / self.speed))  # Prevent division by zero
        self.frame_counter = 0

        self.invincible_to: list[pygame.Rect] = []
        self.max_invincible_entries = 100

        self.sprite = SpriteFromSheet(
            0, 0, 32, 32, self.scale, "assets/sprites/player.png"
        )
        self.rect = self.sprite.sprite.get_rect(center=pos)
        self.hitbox = pygame.Rect(8 * scale, 8 * scale, 8 * scale, 8 * scale)

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.sprite.sprite, self.rect)

    def update_anim(self) -> None:
        self.frame_counter += 1
        if self.frame_counter >= self.anim_timer:
            self.frame_counter = 0
            self.anim_frame = (self.anim_frame + 1) % len(self.anims)
            self.sprite = self.anims[self.anim_frame]

    def follow_target(self, target: pygame.Rect) -> None:
        if not target:
            return

        dx = target.centerx - self.rect.centerx
        dy = target.centery - self.rect.centery
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > self.speed:
            if distance > 0:
                dx = (dx / distance) * self.speed
                dy = (dy / distance) * self.speed

                self.pos[0] += dx
                self.pos[1] += dy
                self.rect.center = (int(self.pos[0]), int(self.pos[1]))

    def take_damage(self, damage: int, rect: Optional[pygame.Rect] = None) -> None:
        if rect and rect in self.invincible_to:
            return

        self.health -= damage

        if rect:
            self.invincible_to.append(rect)

            if len(self.invincible_to) > self.max_invincible_entries:
                self.invincible_to.pop(0)

    def is_dead(self) -> bool:
        return self.health <= 0

    def cleanup(self) -> None:
        self.invincible_to.clear()

    def update(self) -> None:
        if self.target:
            self.follow_target(self.target)
        self.update_anim()

    def follow_target(self, target: pygame.Rect) -> None:
        if not target:
            return

        dx = target.centerx - self.rect.centerx
        dy = target.centery - self.rect.centery
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > self.speed:
            if distance > 0:
                dx = (dx / distance) * self.speed
                dy = (dy / distance) * self.speed

                self.pos[0] += dx
                self.pos[1] += dy
                self.rect.center = (int(self.pos[0]), int(self.pos[1]))
                self.hitbox.center = self.pos
                self.hitbox.y += 8 * self.scale
