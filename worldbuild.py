import numpy
import random
from game import Wall, Hole, Box, Floor
import pygame


def worldbuild(s):
    world_map = numpy.empty((s, s), dtype='U5')
    for y in range(s):
        for x in range(s):
            if not y or y == s - 1 or not x or x == s - 1:
                world_map[y][x] = 'wall'
            else:
                ii = 20
                i = random.randint(-ii, ii)
                if i == -ii:
                    world_map[y][x] = 'hole'
                elif i == ii:
                    world_map[y][x] = 'box'
                else:
                    world_map[y][x] = 'floor'
    return world_map


def worldbuild2(s):
    all_sprites = pygame.sprite.Group()
    world_map = numpy.empty((s, s), dtype=object)
    for y in range(s):
        for x in range(s):
            if not y or y == s - 1 or not x or x == s - 1:
                world_map[y][x] = Wall(x, y)
            else:
                ii = 20
                i = random.randint(-ii, ii)
                if i == -ii:
                    world_map[y][x] = Hole(x, y)
                elif i == ii:
                    world_map[y][x] = Box(x, y)
                else:
                    world_map[y][x] = Floor(x, y)
            all_sprites.add(world_map[y][x])
    return world_map, all_sprites

