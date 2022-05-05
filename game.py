import random
from abc import ABC, abstractmethod
from enum import Enum, auto
import pygame
import os
import numpy as np

COORDINATES = 1000
FPS = 60
SACREDCOW = 19
ZONES = 33
GRID_STEP = 50
PIXEL_STEP = GRID_STEP // 10
HOSC = 9
CLUBTWENTYWHAT = 25
ANIMATION = 10


pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((COORDINATES, COORDINATES))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()

game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'img')
player_img = pygame.image.load(os.path.join(img_folder, 'player.png')).convert()
wall_img = pygame.image.load(os.path.join(img_folder, 'wall.png')).convert()
box_img = pygame.image.load(os.path.join(img_folder, 'box.png')).convert()
floor_img = pygame.image.load(os.path.join(img_folder, 'floor.png')).convert()
hole_img = pygame.image.load(os.path.join(img_folder, 'hole.png')).convert()


subwalls = ['hole', 'box']


tmp_pos = [1, 1]  # YX


class Game:
    def __init__(self):
        self.world, self.ambientsprites = self.worldbuild2(ZONES)
        self.playersprite = pygame.sprite.Group()
        self.playersprite.add(Player(self))
        self.state = PlayerState.IDLE
        self.i = ANIMATION
        self.pos = np.array([1, 1])
        self.region = self.getregion(self.pos)
        self.next_region = self.getregion(self.pos)

    def step(self):
        self.ambientsprites.update()
        self.ambientsprites.draw(screen)
        self.playersprite.update()
        self.playersprite.draw(screen)
        pygame.draw.rect(screen, (237, 216, 255), (0, 0, 25, 1000))
        pygame.draw.rect(screen, (237, 216, 255), (0, 0, 1000, 25))
        pygame.draw.rect(screen, (237, 216, 255), (975, 0, 1000, 1000))
        pygame.draw.rect(screen, (237, 216, 255), (0, 975, 1000, 1000))
        pygame.display.flip()

    def getnextstate(self):
        keystate = pygame.key.get_pressed()
        # print(self.region, self.pos)
        if keystate[pygame.K_a]:
            self.state = PlayerState.LEFT
        elif keystate[pygame.K_d]:
            self.state = PlayerState.RIGHT
        elif keystate[pygame.K_s]:
            self.state = PlayerState.DOWN
        elif keystate[pygame.K_w]:
            self.state = PlayerState.UP
        else:
            self.state = PlayerState.IDLE

    def iswall(self):
        x, y = Dir[self.state] + self.pos
        return not isinstance(self.world[x, y], Floor)

    def run(self):
        running = True
        while running:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            if self.i == 0:
                self.getnextstate()
                if self.iswall():
                    self.state = PlayerState.IDLE
                else:
                    self.region = self.getregion(self.pos)
                    self.pos += Dir[self.state]
                    self.next_region = self.getregion(self.pos)
                self.i = ANIMATION
            else:
                self.step()
                self.i -= 1
        pygame.quit()

    def worldbuild2(self, s):
        all_sprites = pygame.sprite.Group()
        world_map = np.empty((s, s), dtype=object)
        for y in range(s):
            for x in range(s):
                if not y or y == s - 1 or not x or x == s - 1:
                    world_map[x][y] = Wall(x, y, self)
                else:
                    ii = 10
                    i = random.randint(-ii, ii)
                    if i == -ii:
                        world_map[x][y] = Hole(x, y, self)
                    elif i == ii:
                        world_map[x][y] = Box(x, y, self)
                    else:
                        world_map[x][y] = Floor(x, y, self)
                all_sprites.add(world_map[x][y])
        return world_map, all_sprites

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
    # TODO: переделать систему зон обзора. Возможно, две системы зон: одна для игрока другая для камеры


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

Dir = {
    PlayerState.IDLE: np.array([0, 0]),
    PlayerState.UP: np.array([0, -1]),
    PlayerState.LEFT: np.array([-1, 0]),
    PlayerState.DOWN: np.array([0, 1]),
    PlayerState.RIGHT: np.array([1, 0]),
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
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        # self.vector = ([0, 0])

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
        vector = self.get_relative_shift(self.game.region, self.game.next_region, self.game.state)
        self.move_once(vector)


class Player(MovableSprite):
    def __init__(self, game):
        MovableSprite.__init__(self, game)
        self.image = player_img
        self.rect = self.image.get_rect()
        self.surf = pygame.Surface((50, 50))
        self.rect.topleft = (75, 75)

    def get_local_relative_shift(self, region, state):
        vector = single_step_dict[state].copy()
        if region in MovableSprite.sides_x:
            vector *= np.array([1, 0])
        elif region in MovableSprite.sides_y:
            vector *= np.array([0, 1])
        elif region == ZoneType.CC:
            vector *= np.array([0, 0])
        return vector


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


class Wall(AmbientSprite):
    def __init__(self, x, y, game):
        AmbientSprite.__init__(self, game)
        self.image = wall_img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * 50 + CLUBTWENTYWHAT, y * 50 + CLUBTWENTYWHAT)
        self.surf = pygame.Surface((50, 50))


class Box(AmbientSprite):
    def __init__(self, x, y, game):
        AmbientSprite.__init__(self, game)
        self.image = box_img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * 50 + CLUBTWENTYWHAT, y * 50 + CLUBTWENTYWHAT)
        self.surf = pygame.Surface((50, 50))


class Floor(AmbientSprite):
    def __init__(self, x, y, game):
        AmbientSprite.__init__(self, game)
        self.image = floor_img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * 50 + CLUBTWENTYWHAT, y * 50 + CLUBTWENTYWHAT)
        self.surf = pygame.Surface((50, 50))


class Hole(AmbientSprite):
    def __init__(self, x, y, game):
        AmbientSprite.__init__(self, game)
        self.image = hole_img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * 50 + CLUBTWENTYWHAT, y * 50 + CLUBTWENTYWHAT)
        self.surf = pygame.Surface((50, 50))


game = Game()
game.run()