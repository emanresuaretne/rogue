import numpy as np
import pygame

import sprites
from .base import BaseObject
from .items import Inventory, BlackMonster, WhiteMonster

Dir = {
    sprites.PlayerState.IDLE: np.array([0, 0]),
    sprites.PlayerState.UP: np.array([0, -1]),
    sprites.PlayerState.LEFT: np.array([-1, 0]),
    sprites.PlayerState.DOWN: np.array([0, 1]),
    sprites.PlayerState.RIGHT: np.array([1, 0]),
}


class AP(pygame.sprite.Sprite):
    def __init__(self, value, max, owner):
        super().__init__()
        self.max = max
        self.value = value
        self.owner = owner
        self.draw_ap()

    def reset_ap(self, new_ap):
        if new_ap <= self.max:
            self.value = new_ap
        self.draw_ap()

    def draw_ap(self):
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


class Player(BaseObject, sprites.Player):
    ANIMATION = 10

    def __init__(self, game):
        sprites.Player.__init__(self, game)

        self.pos = np.array([1, 1])

        self.region = self.game.getregion(self.pos)
        self.next_region = self.game.getregion(self.pos)

        self.ap = AP(10, 10, self)

        self.state = sprites.PlayerState.IDLE
        self.moves_count = 0

        self.inventory = Inventory(max_slots=5)
        self.inventory.add(BlackMonster())
        self.inventory.add(WhiteMonster())

    def get_next_action(self):
        keystate = pygame.key.get_pressed()

        if keystate[pygame.K_a]:
            state = sprites.PlayerState.LEFT
        elif keystate[pygame.K_d]:
            state = sprites.PlayerState.RIGHT
        elif keystate[pygame.K_s]:
            state = sprites.PlayerState.DOWN
        elif keystate[pygame.K_w]:
            state = sprites.PlayerState.UP
        else:
            state = sprites.PlayerState.IDLE

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
            if keystate[pygame.K_e]:
                active_item.consume(self)


        self.state = state
        return state

    def interact(self, other: "BaseObject"):
        if not isinstance(other, sprites.Floor):
            self.state = sprites.PlayerState.IDLE
            self.moves_count = 0
        elif self.state != sprites.PlayerState.IDLE:
            self.moves_count = self.ANIMATION - 1
            self.region = self.game.getregion(self.pos)
            self.pos += Dir[self.state]
            self.next_region = self.game.getregion(self.pos)

    def update(self):
        if self.state != sprites.PlayerState.IDLE and self.moves_count > 0:
            self.moves_count -= 1

            self.ap.draw_ap()
            sprites.Player.update(self)
        elif self.moves_count == 0 and self.ap.value > 0:
            if self.state != sprites.PlayerState.IDLE:
                self.ap.reset_ap(self.ap.value - 1)
                print(f"AP: {self.ap.value}")
            self.state = sprites.PlayerState.IDLE
            next_action = self.get_next_action()
            next_object = self.game.get_nearby_object(self, next_action)
            self.interact(next_object)
            self.ap.draw_ap()
            sprites.Player.update(self)



