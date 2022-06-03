import abc
import math

import numpy as np
import pygame
import random

import sprites
from . import items
from .base import BaseObject
from .items import Inventory, BlackMonster, WhiteMonster, DiamondSword, Consumable

from pathlib import Path

game_folder = Path(__file__).parent.parent
img_folder = game_folder / 'img'

Dir = {
    sprites.CharacterState.IDLE: np.array([0, 0]),
    sprites.CharacterState.UP: np.array([0, -1]),
    sprites.CharacterState.LEFT: np.array([-1, 0]),
    sprites.CharacterState.DOWN: np.array([0, 1]),
    sprites.CharacterState.RIGHT: np.array([1, 0]),
}


class AP(pygame.sprite.Sprite):
    def __init__(self, value, max, owner, transparent=True):
        super().__init__()
        self.max = max
        self.value = value
        self.owner = owner
        self.transparent = transparent
        self.draw_ap()

    def reset_ap(self, new_ap):
        if new_ap <= self.max:
            self.value = new_ap
        self.draw_ap()

    def draw_ap(self):
        if not self.transparent:
            digit1 = self.value % 10 if self.value < 10 else self.value // 10
            digit2 = None if self.value < 10 else self.value % 10
            pic1 = sprites.img_folder / (f"number{digit1}.png" if digit1 is not None else "player1.png")
            pic2 = sprites.img_folder / (f"number{digit2}.png" if digit2 is not None else "player1.png")
            self.image1 = pygame.image.load(pic1).convert()
            self.image2 = pygame.image.load(pic2).convert()
            self.image1.set_colorkey((0, 0, 0))
            self.image2.set_colorkey((0, 0, 0))
            if digit2 is None:
                self.image2.set_alpha(0)
            else:
                self.image2.set_alpha(255)
            self.rect1 = self.image1.get_rect()
            self.rect1.topleft = (25, 25)
            self.rect2 = self.image2.get_rect()
            self.rect2.topleft = (75, 25)
            self.surf1 = pygame.Surface((50, 50))
            self.surf2 = pygame.Surface((50, 50))
            self.owner.game.screen.blit(self.image1, self.rect1)
            self.owner.game.screen.blit(self.image2, self.rect2)


class HP(pygame.sprite.Sprite):
    def __init__(self, value, max, owner, transparent=True):
        super().__init__()
        self.max = max
        self.value = value
        self.owner = owner
        self.transparent = transparent
        self.draw_hp()

    def draw_hp(self):
        if not self.transparent:
            digit1 = self.value % 10 if self.value < 10 else self.value // 10
            digit2 = None if self.value < 10 else self.value % 10
            pic1 = sprites.img_folder / (f"hp{digit1}.png" if digit1 is not None else "player1.png")
            pic2 = sprites.img_folder / (f"hp{digit2}.png" if digit2 is not None else "player1.png")
            self.image1 = pygame.image.load(pic1).convert()
            self.image2 = pygame.image.load(pic2).convert()
            self.image1.set_colorkey((0, 0, 0))
            self.image2.set_colorkey((0, 0, 0))
            if digit2 is None:
                self.image2.set_alpha(0)
            else:
                self.image2.set_alpha(255)
            self.rect1 = self.image1.get_rect()
            self.rect1.topleft = (25 + 17 * 50, 25)
            self.rect2 = self.image2.get_rect()
            self.rect2.topleft = (25 + 18 * 50, 25)
            self.surf1 = pygame.Surface((50, 50))
            self.surf2 = pygame.Surface((50, 50))
            self.owner.game.screen.blit(self.image1, self.rect1)
            self.owner.game.screen.blit(self.image2, self.rect2)

    def reset_hp(self, new_ap):
        if new_ap <= self.max:
            self.value = new_ap
        self.draw_hp()


class DamageSprite(pygame.sprite.Sprite):
    def __init__(self, value, ttl, owner):
        super().__init__()
        self.value = value
        self.owner = owner
        self.max_ttl = ttl
        self.ttl = 0

    def reset_ttl(self):
        self.ttl = self.max_ttl

    def show_once(self):
        digit1 = self.value % 10 if self.value < 10 else self.value // 10
        digit2 = None if self.value < 10 else self.value % 10
        pic1 = sprites.img_folder / (f"enemyhp{digit1}.png" if digit1 is not None else "enemyhp0.png")
        pic2 = sprites.img_folder / (f"enemyhp{digit2}.png" if digit2 is not None else "enemyhp0.png")
        self.image1 = pygame.image.load(pic1).convert()
        self.image2 = pygame.image.load(pic2).convert()
        self.image1.set_colorkey((0, 0, 0))
        self.image2.set_colorkey((0, 0, 0))
        if digit2 is None:
            self.image2.set_alpha(0)
        else:
            self.image2.set_alpha(255)
        self.rect1 = self.image1.get_rect()
        self.rect1.topleft = (self.owner.rect.x, self.owner.rect.y - 30)
        self.rect2 = self.image2.get_rect()
        self.rect2.topleft = (self.owner.rect.x + 25, self.owner.rect.y - 30)
        self.surf1 = pygame.Surface((50, 50))
        self.surf2 = pygame.Surface((50, 50))

        if self.ttl > 0:
            self.ttl -= 1
        if self.ttl == 0:
            self.image1.set_alpha(0)
            self.image2.set_alpha(0)

        self.owner.game.screen.blit(self.image1, self.rect1)
        self.owner.game.screen.blit(self.image2, self.rect2)


class Character(BaseObject):
    ANIMATION = 10

    def __init__(self, x, y, game, ap_transparency=True):
        self.is_active = False
        self.pos = np.array([x, y])
        self.game = game

        self.region = self.game.getregion(self.pos)
        self.next_region = self.game.getregion(self.pos)

        self.ap = AP(10, 10, self, ap_transparency)
        self.hp = HP(50, 50, self, ap_transparency)
        self.damage = DamageSprite(0, 5, self)

        self.state = sprites.CharacterState.IDLE
        self.moves_count = 0

        self.inventory = Inventory(max_slots=5)

    def update(self):
        if self.is_active:
            if self.moves_count > 0:
                self.moves_count -= 1
                self.image = self.get_image()
            elif self.moves_count == 0:
                self.reset_ap()
                next_action = self.get_next_action()
                next_object = self.game.get_nearby_object(self, next_action)
                if self.ap.value != 0:
                    self.interact(next_object)
                else:
                    self.state = sprites.CharacterState.IDLE
            else:
                assert False, "moves_count < 0"
        else:
            self.state = sprites.CharacterState.IDLE
        self.damage.show_once()
        self.ap.draw_ap()
        self.hp.draw_hp()
        super().update()

    def interact(self, other: "BaseObject"):
        if isinstance(other, sprites.EnemySprite)\
                or isinstance(other, Player):
            self.attack_enemy(other)
            self.state = sprites.CharacterState.IDLE
            self.moves_count = self.ANIMATION - 1
        elif not isinstance(other, sprites.Floor):
            self.state = sprites.CharacterState.IDLE
            if isinstance(self, Enemy):
                self.moves_count = self.ANIMATION - 1
            else:
                self.moves_count = 0
        elif self.state != sprites.CharacterState.IDLE:
            self.moves_count = self.ANIMATION - 1
            self.region = self.game.getregion(self.pos)
            self.pos += Dir[self.state]
            self.next_region = self.game.getregion(self.pos)

    def attack_enemy(self, enemy):
        active_item = self.inventory.active_item
        if isinstance(active_item, items.Weapon) and self.ap.value >= active_item.ap:
            distance = math.hypot(self.rect.centerx - enemy.rect.centerx, self.rect.centery - enemy.rect.centery) / 50
            if distance <= active_item.range:
                # print(f"{self} attacked {enemy} with {active_item.name}")
                # print(f"this consumed {active_item.ap} APs")
                self.ap.reset_ap(self.ap.value - active_item.ap)
                enemy.take_damage(active_item.damage)

    def take_damage(self, damage):
        self.show_damage(damage)
        if damage > self.hp.value:
            self.kill()
        else:
            self.hp.reset_hp(self.hp.value - damage)

        # print(f"shit, got {damage} HP hit")

    def show_damage(self, damage):
        self.damage.value = damage
        self.damage.reset_ttl()


class Enemy(Character, sprites.EnemySprite):
    def __init__(self, x, y, game):
        sprites.EnemySprite.__init__(self, x, y, game)
        Character.__init__(self, x, y, game)
        # self.state = sprites.CharacterState.LEFT

    def get_next_action(self):
        x, y = (self.game.player.pos - self.pos)
        if abs(x) < abs(y):
            if y < 0:
                self.state = sprites.CharacterState.UP
            else:
                self.state = sprites.CharacterState.DOWN
        else:
            if x < 0:
                self.state = sprites.CharacterState.LEFT
            else:
                self.state = sprites.CharacterState.RIGHT
        return self.state

    def reset_ap(self):
        self.ap.reset_ap(self.ap.value - 1)
        # print(f"enemy AP: {self.ap.value}")

    def get_damage(self):
        return random.randint(5, 15)

    def attack_enemy(self, enemy):
        damage = self.get_damage()
        # print(f"{self} attacked {enemy}")
        # print(f"this consumed 1 APs")
        self.ap.reset_ap(self.ap.value - 1)
        enemy.take_damage(damage)


class Player(Character, sprites.Player):
    ANIMATION = 10

    def __init__(self, game):
        Character.__init__(self, 1, 1, game, ap_transparency=False)
        sprites.Player.__init__(self, game)

        self.inventory.add(BlackMonster())
        self.inventory.add(WhiteMonster())
        self.inventory.add(DiamondSword())

    def get_next_action(self):
        keystate = pygame.key.get_pressed()

        if keystate[pygame.K_a]:
            state = sprites.CharacterState.LEFT
        elif keystate[pygame.K_d]:
            state = sprites.CharacterState.RIGHT
        elif keystate[pygame.K_s]:
            state = sprites.CharacterState.DOWN
        elif keystate[pygame.K_w]:
            state = sprites.CharacterState.UP
        else:
            state = sprites.CharacterState.IDLE

        if keystate[pygame.K_1]:
            self.inventory.select_active_item(0)
        elif keystate[pygame.K_2]:
            self.inventory.select_active_item(1)
        elif keystate[pygame.K_3]:
            self.inventory.select_active_item(2)
        elif keystate[pygame.K_4]:
            self.inventory.select_active_item(3)
        elif keystate[pygame.K_5]:
            self.inventory.select_active_item(4)
        elif keystate[pygame.K_q]:
            self.inventory.select_active_item(None)
        active_item = self.inventory.active_item
        if active_item is not None:
            if keystate[pygame.K_e] and isinstance(active_item, Consumable):
                active_item.consume(self)

        self.state = state
        return state

    def reset_ap(self):
        if self.state != sprites.CharacterState.IDLE:
            self.ap.reset_ap(self.ap.value - 1)
            # print(f"player AP: {self.ap.value}")
