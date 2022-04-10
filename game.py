import pygame
import os

import worldbuild
import pov

COORDINATES = 1000
FPS = 60
SACREDCOW = 19
ZONES = 33

colours = {
    'violet': (205, 205, 255),
    'gold': (255, 190, 0),
    'cyan': (0, 165, 185),
    'black': (0, 0, 0)
}

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


def pos_50(pos):
    return pos[0] // 50, pos[1] // 50


subwalls = ['hole', 'box']

# def playerfinder(w):
#     l = []
#     for y, line in enumerate(w):
#         if 'player' in line:
#             for x, obj in enumerate(line):
#                 if obj == 'player':
#                     l = [y, x]
#                     break
#             break
#     return l
# Не нравится, что player взаимодействует с world

tmp_pos = [1, 1]  # YX


# world[tmp_pos[1]][tmp_pos[0]] = 'player'  # YX
# Не нравится, что player взаимодействует с world


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = player_img
        # self.image.set_colorkey(colours['black'])
        # Пока не нужно
        self.rect = self.image.get_rect()

        hosc = (SACREDCOW - 1) // 2

        if tmp_pos[1] < hosc and tmp_pos[0] < hosc:  # LU
            self.rect.topleft = (50 * tmp_pos[1] + 25, 50 * tmp_pos[0] + 25)
        elif ZONES - hosc > tmp_pos[1] >= hosc > tmp_pos[0]:  # CU
            self.rect.topleft = (50 * hosc + 25, 50 * tmp_pos[0] + 25)
        elif ZONES - hosc <= tmp_pos[1] and tmp_pos[0] < hosc:  # RU
            self.rect.topleft = (50 * (tmp_pos[1] + SACREDCOW - ZONES) + 25, 50 * tmp_pos[0] + 25)
        elif tmp_pos[1] < hosc <= tmp_pos[0] < ZONES - hosc:  # LС
            self.rect.topleft = (50 * tmp_pos[1] + 25, 50 * hosc + 25)
        elif tmp_pos[1] >= ZONES - hosc > tmp_pos[0] >= hosc:  # RC
            self.rect.topleft = (50 * (tmp_pos[1] + SACREDCOW - ZONES) + 25, 50 * hosc + 25)
        elif tmp_pos[1] < hosc and ZONES - hosc <= tmp_pos[0]:  # LD
            self.rect.topleft = (50 * tmp_pos[1] + 25, 50 * (tmp_pos[0] + SACREDCOW - ZONES) + 25)
        elif hosc <= tmp_pos[1] < ZONES - hosc <= tmp_pos[0]:  # CD
            self.rect.topleft = (50 * hosc + 25, 50 * (tmp_pos[0] + SACREDCOW - ZONES) + 25)
        elif ZONES - hosc <= tmp_pos[1] and ZONES - hosc <= tmp_pos[0]:  # RD
            self.rect.topleft = (50 * (tmp_pos[1] + SACREDCOW - ZONES) + 25, 50 * (tmp_pos[0] + SACREDCOW - ZONES) + 25)
        else:  # CC
            self.rect.topleft = (50 * hosc + 25, 50 * hosc + 25)

        self.surf = pygame.Surface((50, 50))

    def update(self):
        def moving(zeroth, first):
            to_check = world[tmp_pos[0] + zeroth][tmp_pos[1] + first]
            if not (to_check in subwalls or to_check == 'wall'):
                if zeroth:
                    pos_y = self.rect.topleft[1] + zeroth * 50
                    pos_y_moving = self.rect.topleft[1]
                    while not self.rect.topleft[1] == pos_y:
                        pos_y_moving += zeroth * 2
                        self.rect.topleft = (self.rect.topleft[0], pos_y_moving)
                        pygame.display.flip()
                        # pygame.draw.rect(screen, colours['violet'], (self.rect.topright[0] - 2, self.rect.topright[1], 50, 50))
                        # это было временное решение
                else:
                    pos_x = self.rect.topleft[0] + first * 50
                    pos_x_moving = self.rect.topleft[0]
                    while not self.rect.topleft[0] == pos_x:
                        pos_x_moving += first * 2
                        self.rect.topleft = (pos_x_moving, self.rect.topleft[1])
                        pygame.display.flip()
                        # pygame.draw.rect(screen, colours['violet'], (self.rect.topright[0] - 2, self.rect.topright[1], 50, 50))
                        # это было временное решение

                tmp_pos[0] += zeroth  # YX
                tmp_pos[1] += first  # YX
                # world[tmp_pos[0]][tmp_pos[1]] = 'floor'  # YX
                # world[tmp_pos[0]][tmp_pos[1]] = 'player'  # YX
                # Не нравится, что player взаимодействует с world

        keystate = pygame.key.get_pressed()

        if keystate[pygame.K_a]:
            moving(0, -1)

        if keystate[pygame.K_d]:
            moving(0, 1)

        if keystate[pygame.K_s]:
            moving(1, 0)

        if keystate[pygame.K_w]:
            moving(-1, 0)


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = wall_img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * 50 + clubtwentywhat, y * 50 + clubtwentywhat)
        self.surf = pygame.Surface((50, 50))

    def update(self):
        pass


clubtwentywhat = 25


class Box(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = box_img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * 50 + clubtwentywhat, y * 50 + clubtwentywhat)
        self.surf = pygame.Surface((50, 50))

    def update(self):
        pass


class Floor(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = floor_img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * 50 + clubtwentywhat, y * 50 + clubtwentywhat)
        self.surf = pygame.Surface((50, 50))

    def update(self):
        pass


class Hole(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = hole_img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * 50 + clubtwentywhat, y * 50 + clubtwentywhat)
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
    all_sprites.add(Player())
    return all_sprites


running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    group().update()
    group().draw(screen)

    # screen.fill(colours['violet'])
    pygame.display.flip()

pygame.quit()
