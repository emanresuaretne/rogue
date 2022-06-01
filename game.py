import random
import time

import pygame
import numpy as np

import logic.player
from sprites import PlayerState, ZoneType, Player, Wall, Box, Floor, Hole

COORDINATES = 1000
FPS = 60
ZONES = 33
HOSC = 9
ANIMATION = 10


pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((COORDINATES, COORDINATES))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()

subwalls = ['hole', 'box']


class Game:
    def __init__(self):
        self.world, self.ambientsprites = self.world_build(ZONES)
        self.screen = screen
        self.player_group = pygame.sprite.Group()
        self.player = logic.player.Player(self)
        self.player_group.add(self.player)
        self.inventory_group = self.player.inventory.sprite_group

    def step(self):
        self.ambientsprites.update()
        self.ambientsprites.draw(screen)
        self.player_group.update()
        self.player_group.draw(screen)
        self.inventory_group.update()
        self.inventory_group.draw(screen)
        pygame.draw.rect(screen, (237, 216, 255), (0, 0, 25, 1000))
        pygame.draw.rect(screen, (237, 216, 255), (0, 0, 1000, 25))
        pygame.draw.rect(screen, (237, 216, 255), (975, 0, 1000, 1000))
        pygame.draw.rect(screen, (237, 216, 255), (0, 975, 1000, 1000))
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            next_actor = self.choose_next_actor()
            if next_actor.ap.value == 0:
                time.sleep(1)
                next_actor.ap.reset_ap(next_actor.ap.max)
            self.step()
        pygame.quit()

    def world_build(self, s):
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

    def get_nearby_object(self, curr_object, new_state):
        new_pos = curr_object.pos + Dir[new_state]
        x, y = new_pos
        return self.world[x, y]

    def choose_next_actor(self):
        return self.player


Dir = {
    PlayerState.IDLE: np.array([0, 0]),
    PlayerState.UP: np.array([0, -1]),
    PlayerState.LEFT: np.array([-1, 0]),
    PlayerState.DOWN: np.array([0, 1]),
    PlayerState.RIGHT: np.array([1, 0]),
}


game = Game()
game.run()
