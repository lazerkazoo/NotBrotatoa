import json
import random
import sys
from time import sleep
from typing import Any, Callable

import pygame
from pygame.rect import Rect

from bullet import Bullet
from enemy import Enemy, preload_animations
from gun import Gun
from player import Player
from sprite_sheet import SpriteFromSheet
from text import Text

# Load data
with open("data/constants.json", "r") as f:
    constants = json.load(f)
    f.close()

with open("data/enemy_types.json", "r") as f:
    enemy_data = json.load(f)
    f.close()

pygame.init()
pygame.display.set_caption("Not Brotatoa")
win: Surface = pygame.display.set_mode((1280, 720), pygame.FULLSCREEN)
clock: Clock = pygame.time.Clock()
constants["width"], constants["height"] = win.get_size()
width, height = constants["width"], constants["height"]
win_rect = win.get_rect()

BG_POS: tuple[int, int] = (-int(0.2 * width / 2), -int(0.2 * height / 2))
PLAYER_POS: tuple[int, int] = (int(width / 2), int(height / 2))
BOTTOM_TEXT_POS: tuple[int, int] = (width // 2, int(height * 0.8))

PLAYER_HEALTH: int = constants["player_health"]
PLAYER_SPEED: int = constants["player_speed"]

LARGE_FONT: int = constants["large_font"]
MEDIUM_FONT: int = constants["medium_font"]
SMALL_FONT: int = constants["small_font"]

FPS: int = constants["fps"]

bg_scale: float = width / 1280
bg: SpriteFromSheet = SpriteFromSheet(64, 64, 256, 144, int(bg_scale * 6), "assets/sprites/environment/background.png")
bg.rect.topleft = BG_POS

player_scale: float = width / 1280
player: Player = Player(int(player_scale * 2), PLAYER_POS)

enemy_scale: float = width / 1280

enemy_types = []

enemy_spawns = [
    "left",
    "right",
    "top",
    "bottom"
]

paused: bool = False

sel_gun: str = "pistol"

for enemy_type, data in enemy_data.items():
    enemy_types.append(enemy_type)

def active() -> None:
    global paused
    sleep(1)

    score = 0
    time_scale = 0

    enemies: list[Enemy] = []
    enemy_rects: list[pygame.Rect] = []
    guns: list[Gun] = []

    gun = Gun(sel_gun)
    guns.append(gun)

    spawn_rate = constants["start_spawn_rate"]
    spawn_timer = spawn_rate*FPS

    player.pos = PLAYER_POS
    player.health = PLAYER_HEALTH

    preload_animations()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    win.fill((0, 0, 0))
                    paused = not paused
        
        if paused:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_q]:
                inactive()
            bottom_txt = Text("(paused) press q to quit, p/esc to resume", SMALL_FONT, "white")
            bottom_txt.rect.center = BOTTOM_TEXT_POS
            bottom_txt.draw(win)
            pygame.display.flip()
            clock.tick(10)
            continue

        time_scale += 1/FPS/4
        
        hp_text = Text("HP: " + str(player.health), SMALL_FONT, "white")
        hp_text.rect.topleft = (width // 96, height // 96)
        
        enemies_text = Text("Enemies: " + str(len(enemies)), SMALL_FONT, "white")
        enemies_text.rect.topleft = (width // 96, height // 96 + SMALL_FONT)

        score_text = Text("Score: " + str(score), SMALL_FONT, "white")
        score_text.rect.topleft = (width // 96, height // 96 + SMALL_FONT * 2)

        spawn_timer -= 1
        if spawn_timer <= 0:
            spawn_timer = spawn_rate*FPS-time_scale
            spawn: str = random.choice(enemy_spawns)
            enemy_type: Any = random.choice(enemy_types)
            
            if spawn == "left":
                en = Enemy(enemy_scale*enemy_data[enemy_type]["scale"], (0, random.randint(0, height)), enemy_type, enemy_data)
                enemies.append(en)
                enemy_rects.append(en.rect)
            elif spawn == "right":
                en = Enemy(enemy_scale*enemy_data[enemy_type]["scale"], (width, random.randint(0, height)), enemy_type, enemy_data)
                enemies.append(en)
                enemy_rects.append(en.rect)
            elif spawn == "top":
                en = Enemy(enemy_scale*enemy_data[enemy_type]["scale"], (random.randint(0, width), 0), enemy_type, enemy_data)
                enemies.append(en)
                enemy_rects.append(en.rect)
            elif spawn == "bottom":
                en = Enemy(enemy_scale*enemy_data[enemy_type]["scale"], (random.randint(0, width), height), enemy_type, enemy_data)
                enemies.append(en)
                enemy_rects.append(en.rect)

        bg.draw(win)

        for gun in guns:
            gun.rate -= 1
            if gun.rate < 0:
                gun.rate = gun.data["rate"]
                gun.shoot(pygame.mouse.get_pos(), player.rect.center)

            bullets_to_remove = []
            for bullet in gun.get_bullets():
                collision_index = bullet.rect.collidelist(enemy_rects)
                if collision_index != -1:
                    if collision_index < len(enemies):
                        enemies[collision_index].take_damage(gun.damage, bullet.rect)
                        bullet.pierce -= 1
                        if bullet.pierce <= 0:
                            bullets_to_remove.append(bullet)

            # Remove bullets that have no pierce remaining
            for bullet in bullets_to_remove:
                gun.bullets.remove(bullet)

            gun.update()
            gun.draw(win)

        enemy_rects: list[Rect] = [enemy.rect for enemy in enemies]

        enemies_to_remove = []
        for enemy in enemies:
            enemy.target = player.rect
            enemy.update()
            enemy.draw(win)

            if enemy.is_dead():
                enemies_to_remove.append(enemy)
                score += enemy.points
            elif enemy.rect.colliderect(player.rect):
                player.take_damage(enemy.damage, inactive)

        for enemy in enemies_to_remove:
            enemy.cleanup()
            enemies.remove(enemy)

        enemy_rects = [enemy.rect for enemy in enemies]

        hp_text.draw(win)
        enemies_text.draw(win)
        score_text.draw(win)

        player.update_pos()
        player.update_anim()
        if player.invinsible_timer > 0:
            player.invinsible_timer -= 1
        player.draw(win)

        pygame.display.flip()
        clock.tick(FPS)


def inactive() -> None:
    bg.rect.topleft = BG_POS

    play_btn = Text("play", LARGE_FONT, "black", "pink")
    play_btn.rect.center = (width // 2, height // 4)

    quit_btn = Text("quit", LARGE_FONT, "black", "pink")
    quit_btn.rect.center = (width // 2, height // 1.5)
    
    player.pos = PLAYER_POS

    button_tooltips: list[tuple[Text, str, int, Callable]] = [
        (play_btn, "Press Space to Start Game", pygame.K_SPACE, choose_gun),
        (quit_btn, "Press Q to Quit Game", pygame.K_q, sys.exit)
    ]

    while True:
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        bg.draw(win)

        for btn, tooltip, event, do in button_tooltips:
            if btn.check_can_press(player.rect):
                if keys[event]:
                    do()
                bottom_txt: Text = Text(tooltip, SMALL_FONT, "grey")
                bottom_txt.rect.center = BOTTOM_TEXT_POS
                bottom_txt.draw(win)

            if btn.rect.collidepoint(pygame.mouse.get_pos()):
                if pygame.mouse.get_pressed()[0] or keys[event]:
                    do()
                bottom_txt: Text = Text(tooltip, SMALL_FONT, "grey")
                bottom_txt.rect.center = BOTTOM_TEXT_POS
                bottom_txt.draw(win)

        play_btn.draw(win)
        quit_btn.draw(win)

        player.update_pos()
        player.update_anim()
        player.draw(win)

        pygame.display.flip()
        clock.tick(FPS)


def choose_gun() -> None:
    top_txt = Text("Select Gun", LARGE_FONT, "black", "pink")
    top_txt.rect.center = (width // 2, height // 4)

    mini_btn = Text("mini", MEDIUM_FONT, "black", "pink")
    mini_btn.rect.center = (width // 3, height // 2)

    pistol_btn = Text("pistol", MEDIUM_FONT, "black", "pink")
    pistol_btn.rect.center = (width // 1.5, height // 2)

    button_tooltips: list[tuple[Text, str, int, Callable, str]] = [
        (mini_btn, "Press Space to Select MiniGun", pygame.K_SPACE, select_gun, "mini"),
        (pistol_btn, "Press Space to Select Pistol", pygame.K_SPACE, select_gun, "pistol")
    ]

    player.pos = PLAYER_POS

    while True:
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        bg.draw(win)

        top_txt.draw(win)
        mini_btn.draw(win)
        pistol_btn.draw(win)

        player.update_pos()
        player.update_anim()
        player.draw(win)

        for btn, tooltip, event, do, gun in button_tooltips:
            if btn.check_can_press(player.rect):
                if keys[event]:
                    do(gun)
                    active()
                bottom_txt: Text = Text(tooltip, SMALL_FONT, "grey")
                bottom_txt.rect.center = BOTTOM_TEXT_POS
                bottom_txt.draw(win)

            if btn.rect.collidepoint(pygame.mouse.get_pos()):
                if pygame.mouse.get_pressed()[0] or keys[event]:
                    do(gun)
                    active()
                bottom_txt: Text = Text(tooltip, SMALL_FONT, "grey")
                bottom_txt.rect.center = BOTTOM_TEXT_POS
                bottom_txt.draw(win)

        pygame.display.flip()
        clock.tick(FPS)

def select_gun(gun: str) -> None:
    global sel_gun
    sel_gun = gun

inactive()

pygame.quit()
