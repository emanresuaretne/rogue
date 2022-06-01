import os
from abc import ABC, abstractmethod
from enum import Enum, auto
from pathlib import Path
import random

import numpy as np
import pygame

GRID_STEP = 50
PIXEL_STEP = GRID_STEP // 10
CLUBTWENTYWHAT = 25

game_folder = Path(__file__).parent
img_folder = game_folder / 'img'


class PlayerState(Enum):
    IDLE = auto()
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    DOWN = auto()


single_step_dict = {
    PlayerState.IDLE: np.array([0, 0]),
    PlayerState.UP: np.array([0, -PIXEL_STEP]),
    PlayerState.LEFT: np.array([-PIXEL_STEP, 0]),
    PlayerState.DOWN: np.array([0, PIXEL_STEP]),
    PlayerState.RIGHT: np.array([PIXEL_STEP, 0]),
}


class ZoneType(Enum):
    LU = auto()
    CU = auto()
    RU = auto()
    LC = auto()
    RC = auto()
    LD = auto()
    CD = auto()
    RD = auto()
    CC = auto()


class MovableSprite(ABC, pygame.sprite.Sprite):
    def __init__(self, x, y, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image = self.get_image()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * 50 + CLUBTWENTYWHAT, y * 50 + CLUBTWENTYWHAT)
        self.surf = pygame.Surface((50, 50))

    def move_once(self, vector):
        x, y = vector
        x = int(x)
        y = int(y)
        self.rect = self.rect.move(x, y)

    @abstractmethod
    def get_local_relative_shift(self, region, state):
        pass

    def get_relative_shift(self, region, next_region, state):
        if region == next_region \
                or (region in self.corners and next_region != region) \
                or (region != next_region and next_region == ZoneType.CC):
            return self.get_local_relative_shift(region, state)
        else:
            return self.get_local_relative_shift(next_region, state)

    corners = (ZoneType.LU, ZoneType.RU, ZoneType.RD, ZoneType.LD)
    sides_x = (ZoneType.RC, ZoneType.LC)
    sides_y = (ZoneType.CU, ZoneType.CD)

    def update(self):
        vector = self.get_relative_shift(
            self.game.player.region,
            self.game.player.next_region,
            self.game.player.state
        )
        self.move_once(vector)

    @abstractmethod
    def get_image(self):
        pass

    def get_random_pic_by_name(self):
        pattern = f"{self.__class__.__name__}*.png"
        choice = random.choice(list(img_folder.glob(pattern)))
        return pygame.image.load(choice).convert()


# class Frame(pygame.sprite.Sprite):
#     def __init__(self, game):
#         pygame.sprite.Sprite.__init__(self)
#         self.game = game
#         self.image = img_folder / 'frame1.png'
#         self.rect = self.image.get_rect()
#         self.rect.topleft = (25, 0)
#         self.surf = pygame.Surface((950, 25))


class Player(MovableSprite):
    def __init__(self, game):
        self.__player_img = pygame.image.load(os.path.join(img_folder, 'player1.png')).convert()
        self.__player_img.set_colorkey((0, 0, 0))
        MovableSprite.__init__(self, 1, 1, game)

    def get_local_relative_shift(self, region, state):
        vector = single_step_dict[state].copy()
        if region in MovableSprite.sides_x:
            vector *= np.array([1, 0])
        elif region in MovableSprite.sides_y:
            vector *= np.array([0, 1])
        elif region == ZoneType.CC:
            vector *= np.array([0, 0])
        return vector

    def get_image(self):
        return self.__player_img


class AmbientSprite(MovableSprite):
    def get_local_relative_shift(self, region, state):
        vector = -(single_step_dict[state].copy())
        if region in MovableSprite.sides_x:
            vector *= np.array([0, 1])
        elif region in MovableSprite.sides_y:
            vector *= np.array([1, 0])
        elif region in MovableSprite.corners:
            vector *= np.array([0, 0])
        return vector

    def get_image(self):
        return self.get_random_pic_by_name()


class Wall(AmbientSprite):
    pass


class Box(AmbientSprite):
    pass


class Floor(AmbientSprite):
    pass


class Hole(AmbientSprite):
    pass
