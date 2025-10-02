import json
import random
import sys
from time import sleep
from typing import Any, Callable

import pygame
from pygame.rect import Rect
from scripts.enemy import Enemy, preload_animations
from scripts.gun import Gun
from scripts.player import Player
from scripts.sprite_sheet import SpriteFromSheet
from scripts.text import Text

# Load data
with open("data/constants.json", "r") as f:
    constants = json.load(f)
    f.close()

with open("data/enemy_types.json", "r") as f:
    enemy_data = json.load(f)
    f.close()

with open("data/gun_upgrades.json", "r") as f:
    gun_upgrades = json.load(f)
    f.close()

pygame.init()
pygame.display.set_caption("Not Brotatoa")
win: pygame.Surface = pygame.display.set_mode((1280, 720), pygame.FULLSCREEN)
clock: pygame.time.Clock = pygame.time.Clock()
constants["width"], constants["height"] = win.get_size()
width, height = constants["width"], constants["height"]
win_rect = win.get_rect()
scalling: float = width / 1280

BG_POS: tuple[int, int] = (-int(0.2 * width / 2), -int(0.2 * height / 2))
PLAYER_POS: tuple[int, int] = (int(width / 2), int(height / 2))
BOTTOM_TEXT_POS: tuple[int, int] = (width // 2, int(height * 0.8))

PLAYER_HEALTH: int = constants["player_health"]
PLAYER_SPEED: int = constants["player_speed"]

LARGE_FONT: int = constants["large_font"]
MEDIUM_FONT: int = constants["medium_font"]
SMALL_FONT: int = constants["small_font"]

FPS: int = constants["fps"]

bg: SpriteFromSheet = SpriteFromSheet(
    64, 64, 256, 144, int(scalling * 6), "assets/sprites/environment/background.png"
)
bg.rect.topleft = BG_POS

player: Player = Player(int(scalling * 2), PLAYER_POS)

enemy_types = []

enemy_spawns = ["left", "right", "top", "bottom"]

paused: bool = False

for enemy_type, data in enemy_data.items():
    enemy_types.append(enemy_type)


def active() -> None:
    global paused
    running = True
    sleep(0.1)

    score = 0
    last_upgrade_score = 0  # Track the score when last upgrade was given

    enemies: list[Enemy] = []
    enemy_rects: list[pygame.Rect] = []
    guns: list[Gun] = []

    gun = Gun(sel_gun)
    guns.append(gun)

    spawn_rate = constants["start_spawn_rate"]
    spawn_timer = spawn_rate * FPS

    player.pos = PLAYER_POS
    player.health = PLAYER_HEALTH

    preload_animations()

    while running:
        enemy_rects: list[pygame.Rect] = [enemy.rect for enemy in enemies]

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
                player.pos = PLAYER_POS
                running = False
                paused = False
            bottom_txt = Text(
                "(paused) press q to quit, p/esc to resume", SMALL_FONT, "white"
            )
            bottom_txt.rect.center = BOTTOM_TEXT_POS
            bottom_txt.draw(win)
            pygame.display.flip()
            clock.tick(10)
            continue

        hp_text = Text("HP: " + str(player.health), SMALL_FONT, "white")
        hp_text.rect.topleft = (width // 96, height // 96)

        enemies_text = Text("Enemies: " + str(len(enemies)), SMALL_FONT, "white")
        enemies_text.rect.topleft = (width // 96, height // 96 + SMALL_FONT)

        score_text = Text("Score: " + str(score), SMALL_FONT, "white")
        score_text.rect.topleft = (width // 96, height // 96 + SMALL_FONT * 2)

        # Give upgrade every 750 points
        if score - last_upgrade_score >= 350:
            last_upgrade_score += 350
            choose_upgrade(gun)

        spawn_timer -= 1
        if spawn_timer <= 0:
            spawn_timer = spawn_rate * FPS - (pow(score, 0.5))
            spawn: str = random.choice(enemy_spawns)
            enemy_type: Any = random.choice(enemy_types)

            if spawn == "left":
                en = Enemy(
                    scalling * enemy_data[enemy_type]["scale"],
                    (0, random.randint(0, height)),
                    enemy_type,
                    enemy_data,
                )
                en.health += score / 100
                enemies.append(en)
                enemy_rects.append(en.rect)
            elif spawn == "right":
                en = Enemy(
                    scalling * enemy_data[enemy_type]["scale"],
                    (width, random.randint(0, height)),
                    enemy_type,
                    enemy_data,
                )
                en.health += score / 100
                enemies.append(en)
                enemy_rects.append(en.rect)
            elif spawn == "top":
                en = Enemy(
                    scalling * enemy_data[enemy_type]["scale"],
                    (random.randint(0, width), 0),
                    enemy_type,
                    enemy_data,
                )
                en.health += score / 100
                enemies.append(en)
                enemy_rects.append(en.rect)
            elif spawn == "bottom":
                en = Enemy(
                    scalling * enemy_data[enemy_type]["scale"],
                    (random.randint(0, width), height),
                    enemy_type,
                    enemy_data,
                )
                en.health += score / 100
                enemies.append(en)
                enemy_rects.append(en.rect)

        bg.draw(win)

        for gun in guns:
            gun.rate -= 1
            if gun.rate < 0:
                gun.rate = gun.data["rate"]
                gun.shoot(pygame.mouse.get_pos(), player.rect.center)

            gun.update()

            for bullet in gun.get_bullets():
                collision_index = bullet.rect.collidelist(enemy_rects)
                if collision_index != -1:
                    if collision_index < len(enemies):
                        enemies[collision_index].take_damage(gun.damage, bullet.rect)
                        bullet.pierce -= 1

            gun.draw(win)

        enemies_to_remove = []

        for enemy in enemies:
            enemy.target = player.rect
            enemy.update()
            enemy.draw(win)

            if enemy.is_dead():
                enemies_to_remove.append(enemy)
                score += enemy.points
            elif enemy.hitbox.colliderect(player.hitbox):
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

        last_score = score

        pygame.display.flip()
        clock.tick(FPS)


def inactive() -> None:
    running = False
    bg.rect.topleft = BG_POS

    play_btn = Text("play", LARGE_FONT, "black", "pink")
    play_btn.rect.center = (width // 2, height // 4)

    quit_btn = Text("quit", LARGE_FONT, "black", "pink")
    quit_btn.rect.center = (width // 2, height // 1.5)

    player.pos = PLAYER_POS

    button_tooltips: list[tuple[Text, str, int, Callable]] = [
        (play_btn, "Press Space to Start Game", pygame.K_SPACE, choose_gun),
        (quit_btn, "Press Q to Quit Game", pygame.K_q, sys.exit),
    ]

    while not running:
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
    choosing = True
    top_txt = Text("Select Gun", LARGE_FONT, "black", "pink")
    top_txt.rect.center = (width // 2, height // 4)

    mini_btn = Text("mini", MEDIUM_FONT, "black", "pink")
    mini_btn.rect.center = (width // 3, height // 2)

    pistol_btn = Text("pistol", MEDIUM_FONT, "black", "pink")
    pistol_btn.rect.center = (width // 1.5, height // 2)

    button_tooltips: list[tuple[Text, str, int, Callable, str]] = [
        (mini_btn, "Press Space to Select MiniGun", pygame.K_SPACE, select_gun, "mini"),
        (
            pistol_btn,
            "Press Space to Select Pistol",
            pygame.K_SPACE,
            select_gun,
            "pistol",
        ),
    ]

    player.pos = PLAYER_POS

    while choosing:
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
                    choosing = False
                    do(gun)
                    active()
                bottom_txt: Text = Text(tooltip, SMALL_FONT, "grey")
                bottom_txt.rect.center = BOTTOM_TEXT_POS
                bottom_txt.draw(win)

            if btn.rect.collidepoint(pygame.mouse.get_pos()):
                if pygame.mouse.get_pressed()[0] or keys[event]:
                    choosing = False
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


def get_upgrades() -> list[str]:
    option1 = random.choice(list(gun_upgrades.keys()))
    option2 = random.choice(list(gun_upgrades.keys()))
    option3 = random.choice(list(gun_upgrades.keys()))

    while option1 == option2 or option1 == option3 or option2 == option3:
        option2 = random.choice(list(gun_upgrades.keys()))
        option3 = random.choice(list(gun_upgrades.keys()))

    options: list[str] = [option1, option2, option3]

    return options


def choose_upgrade(gun: Gun) -> None:
    top_txt = Text("Choose An Upgrade", LARGE_FONT, "white")
    top_txt.rect.center = (width / 2, height / 4)

    left_option = Text("left", SMALL_FONT, "white")
    left_option.rect.center = (width / 3, height / 2)

    middle_option = Text("middle", SMALL_FONT, "white")
    middle_option.rect.center = (width / 2, height / 1.5)

    right_option = Text("right", SMALL_FONT, "white")
    right_option.rect.center = (width / 1.5, height / 2)

    options = [left_option, middle_option, right_option]

    choosing = True
    upgrade_buttons: list[tuple[Text, str, str, str]] = []
    upgrades = get_upgrades()
    upgrade_num = 0
    for item, upgrade in gun_upgrades.items():
        for i in upgrades:
            if item == i:
                upgrade_buttons.append(
                    (
                        options[upgrade_num],
                        item,
                        upgrade["change_by"],
                        upgrade["description"],
                    )
                )
                options[upgrade_num].text = item
                options[upgrade_num].update_txt()
                upgrade_num += 1

    while choosing:
        btm_txt = "Press ESC to Cancel"
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    choosing = False

        win.fill("black")

        top_txt.draw(win)
        for textvar, to_change, change, desk in upgrade_buttons:
            textvar.draw(win)
            if textvar.rect.collidepoint(pygame.mouse.get_pos()):
                if pygame.mouse.get_pressed()[0]:
                    setattr(gun, to_change, (getattr(gun, to_change) + change))
                    choosing = False
                btm_txt = desk

        bottom_txt = Text(btm_txt, SMALL_FONT, "grey")
        bottom_txt.rect.center = (width / 2, height / 1.25)
        bottom_txt.draw(win)

        pygame.display.flip()


inactive()

pygame.quit()
sys.exit()
