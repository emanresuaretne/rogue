import random


def worldbuild(s):
    world_map = []
    for y in range(s):
        line = []
        for x in range(s):
            if not y or y == s - 1 or not x or x == s - 1:
                line.append('wall')
            else:
                ii = 4
                i = random.randint(-ii, ii)
                if i == -ii:
                    line.append('hole')
                elif i == ii:
                    line.append('box')
                else:
                    line.append('floor')
        world_map.append(line)
    return world_map
