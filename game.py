import random
import time
from itertools import chain, islice
from typing import Optional, Tuple

import numpy as np
import pygame

import logic.player
from logic import player
from sprites import (
    CharacterState,
    ZoneType,
    Wall,
    Box,
    Floor,
    Hole,
    EnemySprite,
    AmbientSprite,
    Outline,
    APFrame,
    HPFrame
)

COORDINATES = 1000
FPS = 60
ZONES = 33
HOSC = 9
ANIMATION = player.Character.ANIMATION
P = 0.005

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((COORDINATES, COORDINATES))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()

subwalls = ['hole', 'box']


class Game:
    def __init__(self):
        (self.world,
         self.ambientsprites,
         self.enemy_sprites) = self.world_build(ZONES, P)

        self.screen = screen
        self.player_group = pygame.sprite.Group()
        self.player = logic.player.Player(self)
        self.outline_group = pygame.sprite.Group()
        self.outline = Outline()
        self.outline_group.add(self.outline)
        self.player_group.add(self.player)
        self.inventory_group = self.player.inventory.sprite_group

        self.frame_group = pygame.sprite.Group()
        self.apframe = APFrame()
        self.hpframe = HPFrame()
        self.frame_group.add(self.apframe)
        self.frame_group.add(self.hpframe)

        self.clicked_on = []

        self.active_sprite = self.player
        self.player.is_active = True
        self.last_chosen_enemy = None

    def step(self):
        for group in [self.ambientsprites,
                      self.player_group,
                      self.enemy_sprites,
                      self.inventory_group,
                      self.outline_group,
                      self.frame_group]:
            group.update()
            group.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    sprite: AmbientSprite
                    self.clicked_on = [
                        sprite for sprite in chain(self.enemy_sprites, self.ambientsprites)
                        if sprite.check_click(event.pos)
                    ]

            next_actor = self.choose_next_actor()
            if next_actor.ap.value == 0:
                time.sleep(1)
                # print("here")
                next_actor.ap.reset_ap(next_actor.ap.max)
            if self.clicked_on:
                pass
                # print(self.clicked_on)
            self.step()
            self.clicked_on = []

        pygame.quit()

    def world_build(self, s, p):
        all_sprites = pygame.sprite.Group()
        enemy_sprites = pygame.sprite.Group()
        world_map = np.empty((s, s), dtype=object)
        enemies_to_generate = 3

        def flip(p):
            return random.random() < p

        for y in range(s):
            for x in range(s):
                if not y or y == s - 1 or not x or x == s - 1:
                    world_map[x][y] = Wall(x, y, self)
                elif (y == 2 or y == 1) and x == 1:
                    world_map[x][y] = Floor(x, y, self)
                else:
                    ii = 1
                    i = random.randint(-ii, ii)
                    if i == -ii and not x % 2 and not y % 2:
                        world_map[x][y] = Hole(x, y, self)
                    elif i == ii and x % 3 and y % 3:
                        world_map[x][y] = Box(x, y, self)
                    else:
                        world_map[x][y] = Floor(x, y, self)
                        if enemies_to_generate > 0 and flip(p):
                            enemies_to_generate -= 1
                            enemy = logic.player.Enemy(x, y, self)
                            enemy_sprites.add(enemy)

                all_sprites.add(world_map[x][y])
        return world_map, all_sprites, enemy_sprites

    @staticmethod
    def getregion(inner_pos):
        if inner_pos[0] < HOSC and inner_pos[1] < HOSC:
            return ZoneType.LU
        elif ZONES - HOSC > inner_pos[0] >= HOSC > inner_pos[1]:
            return ZoneType.CU
        elif ZONES - HOSC <= inner_pos[0] and inner_pos[1] < HOSC:
            return ZoneType.RU
        elif inner_pos[0] < HOSC <= inner_pos[1] < ZONES - HOSC:
            return ZoneType.LC
        elif inner_pos[0] >= ZONES - HOSC > inner_pos[1] >= HOSC:
            return ZoneType.RC
        elif inner_pos[0] < HOSC and ZONES - HOSC <= inner_pos[1]:
            return ZoneType.LD
        elif HOSC <= inner_pos[0] < ZONES - HOSC <= inner_pos[1]:
            return ZoneType.CD
        elif ZONES - HOSC <= inner_pos[0] and ZONES - HOSC <= inner_pos[1]:
            return ZoneType.RD
        else:
            return ZoneType.CC

    def get_nearby_object(self, curr_object, new_state):
        if self.clicked_on:
            return self.clicked_on[0]
        new_pos = curr_object.pos + Dir[new_state]
        if isinstance(curr_object, player.Enemy) and (new_pos == self.player.pos).all():
            return self.player
        x, y = new_pos
        return self.world[x, y]

    def choose_next_actor(self):
        if self.active_sprite.ap.value == 0:
            self.active_sprite.is_active = False
            if self.active_sprite == self.player and self.enemy_sprites:
                for enemy in self.enemy_sprites:
                    self.active_sprite = enemy
                    self.last_chosen_enemy = 0
                    break
            elif self.last_chosen_enemy is not None \
                    and len(self.enemy_sprites) - self.last_chosen_enemy - 1 > 0:
                for enemy in islice(self.enemy_sprites, self.last_chosen_enemy + 1, None):
                    self.active_sprite = enemy
                    self.last_chosen_enemy += 1
                    break
            else:
                self.active_sprite = self.player
                self.last_chosen_enemy = None

            # print(f"active sprite set to {self.active_sprite}")
        self.active_sprite.is_active = True
        return self.active_sprite


Dir = {
    CharacterState.IDLE: np.array([0, 0]),
    CharacterState.UP: np.array([0, -1]),
    CharacterState.LEFT: np.array([-1, 0]),
    CharacterState.DOWN: np.array([0, 1]),
    CharacterState.RIGHT: np.array([1, 0]),
}

game = Game()
game.run()
