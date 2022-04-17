import time
from enum import Enum, auto
import pygame
import os
import worldbuild
import pov

COORDINATES = 1000
FPS = 60
SACREDCOW = 19
ZONES = 33
GRID_STEP = 50
PIXEL_STEP = GRID_STEP // 10
HOSC = (SACREDCOW - 1) // 2
CLUBTWENTYWHAT = 25
ANIMATION = 10

# colours = {
#     'violet': (205, 205, 255),
#     'gold': (255, 190, 0),
#     'cyan': (0, 165, 185),
#     'black': (0, 0, 0)
# }

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

world = worldbuild.worldbuild(ZONES)


# def pos_50(pos):
#     return pos[0] // 50, pos[1] // 50


subwalls = ['hole', 'box']


tmp_pos = [1, 1]  # YX


class PlayerState(Enum):
    IDLE = auto()
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    DOWN = auto()


def to_yx(xy: pygame.Rect):
    x, y = xy.topleft
    x = (x - 25) // GRID_STEP
    y = (y - 25) // GRID_STEP
    return y, x


class Player(pygame.sprite.Sprite):
    @staticmethod
    def coors_to_screen(inner_pos):
        if inner_pos[1] < HOSC and inner_pos[0] < HOSC:  # LU
            return 50 * inner_pos[1] + 25, 50 * inner_pos[0] + 25
        elif ZONES - HOSC > inner_pos[1] >= HOSC > inner_pos[0]:  # CU
            return 50 * HOSC + 25, 50 * inner_pos[0] + 25
        elif ZONES - HOSC <= inner_pos[1] and inner_pos[0] < HOSC:  # RU
            return 50 * (inner_pos[1] + SACREDCOW - ZONES) + 25, 50 * inner_pos[0] + 25
        elif inner_pos[1] < HOSC <= inner_pos[0] < ZONES - HOSC:  # LС
            return 50 * inner_pos[1] + 25, 50 * HOSC + 25
        elif inner_pos[1] >= ZONES - HOSC > inner_pos[0] >= HOSC:  # RC
            return 50 * (inner_pos[1] + SACREDCOW - ZONES) + 25, 50 * HOSC + 25
        elif inner_pos[1] < HOSC and ZONES - HOSC <= inner_pos[0]:  # LD
            return 50 * inner_pos[1] + 25, 50 * (inner_pos[0] + SACREDCOW - ZONES) + 25
        elif HOSC <= inner_pos[1] < ZONES - HOSC <= inner_pos[0]:  # CD
            return 50 * HOSC + 25, 50 * (inner_pos[0] + SACREDCOW - ZONES) + 25
        elif ZONES - HOSC <= inner_pos[1] and ZONES - HOSC <= inner_pos[0]:  # RD
            return 50 * (inner_pos[1] + SACREDCOW - ZONES) + 25, 50 * (inner_pos[0] + SACREDCOW - ZONES) + 25
        else:  # CC
            return 50 * HOSC + 25, 50 * HOSC + 25

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = player_img
        self.rect = self.image.get_rect()
        self.surf = pygame.Surface((50, 50))
        self.rect.topleft = (75, 75)
        self.next_pos = self.rect
        self.player_state = PlayerState.IDLE
        self.delta = pygame.math.Vector2(0, 0)
        self.next_vec = pygame.math.Vector2(self.rect.topleft)
        self.i = 0

    def move_once(self):
        x, y = self.delta.xy
        x = int(x)
        y = int(y)
        self.rect = self.rect.move(x, y)
        if self.i == 0:
            self.player_state = PlayerState.IDLE
            global tmp_pos
            tmp_pos = self.next_pos
            self.delta = pygame.math.Vector2(0, 0)
        else:
            self.i -= 1
        # if pygame.math.Vector2(*self.rect.topleft) == self.next_vec:

    def update(self):
        if self.player_state == PlayerState.IDLE:
            keystate = pygame.key.get_pressed()

            next_pos = tmp_pos[:]
            if keystate[pygame.K_a]:
                self.player_state = PlayerState.LEFT
                next_pos[1] -= 1
            elif keystate[pygame.K_d]:
                self.player_state = PlayerState.RIGHT
                next_pos[1] += 1
            elif keystate[pygame.K_s]:
                self.player_state = PlayerState.DOWN
                next_pos[0] += 1
            elif keystate[pygame.K_w]:
                self.player_state = PlayerState.UP
                next_pos[0] -= 1

            # next_pos = self.rect.move(*step_dict[self.player_state])
            y, x = next_pos
            to_check = world[y][x]
            if to_check in subwalls or to_check == 'wall':
                self.player_state = PlayerState.IDLE
            else:
                self.next_pos = next_pos
                self.next_vec = pygame.math.Vector2(*self.coors_to_screen(next_pos))
                curr_vec = pygame.math.Vector2(*self.rect.topleft)
                self.delta = (self.next_vec - curr_vec) / ANIMATION
                self.i = ANIMATION - 1
        else:
            self.move_once()


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = wall_img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * 50 + CLUBTWENTYWHAT, y * 50 + CLUBTWENTYWHAT)
        self.surf = pygame.Surface((50, 50))

    def update(self):
        pass


class Box(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = box_img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * 50 + CLUBTWENTYWHAT, y * 50 + CLUBTWENTYWHAT)
        self.surf = pygame.Surface((50, 50))

    def update(self):
        pass


class Floor(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = floor_img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * 50 + CLUBTWENTYWHAT, y * 50 + CLUBTWENTYWHAT)
        self.surf = pygame.Surface((50, 50))

    def update(self):
        pass


class Hole(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = hole_img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * 50 + CLUBTWENTYWHAT, y * 50 + CLUBTWENTYWHAT)
        self.surf = pygame.Surface((50, 50))

    def update(self):
        pass


def group():
    all_sprites = pygame.sprite.Group()
    for y, line in enumerate(pov.pov(tmp_pos, world, SACREDCOW)):
        for x, place in enumerate(line):
            if place == 'wall':
                all_sprites.add(Wall(x, y))
            if place == 'box':
                all_sprites.add(Box(x, y))
            if place == 'floor':
                all_sprites.add(Floor(x, y))
            if place == 'hole':
                all_sprites.add(Hole(x, y))
    # all_sprites.add(Player())
    return all_sprites

playersprite = pygame.sprite.Group()
playersprite.add(Player())

running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    group().update()
    group().draw(screen)
    playersprite.update()
    playersprite.draw(screen)

    pygame.display.flip()

pygame.quit()
