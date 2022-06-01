import abc
from typing import List, Optional

import pygame.sprite

# from .player import Player
import sprites


class InventoryMainSprite:
    pass


class Frame(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = self.get_image()
        self.rect = self.image.get_rect()
        self.rect.topleft = (75, 25)
        self.surf = pygame.Surface((50, 50))
        self.select(None)

    def select(self, index: Optional[int]):
        if index is None:
            self.image.set_alpha(0)
        else:
            self.rect.topleft = ((index + 2) * 50 + 25, 25)
            self.image.set_colorkey((255, 255, 255))
            self.image.set_alpha(255)


    def get_image(self):
        return pygame.image.load(sprites.img_folder / "frame.png").convert()


class Inventory:
    def __init__(self, max_slots: int):
        self.max_slots = max_slots
        self.inventory: List[Optional["Item"]] = [None] * self.max_slots
        self.active_item: Optional["Item"] = None
        self.sprite_group = pygame.sprite.Group()
        self.frame = Frame()
        self.sprite_group.add(self.frame)

    def remove(self, item: "Item"):
        for i in range(len(self.inventory)):
            if self.inventory[i] == item:
                if self.active_item == item:
                    self.active_item = None
                    self.frame.select(None)
                item.sprite.kill()
                self.inventory[i] = None

    def add(self, item: "Item"):
        for i, el in enumerate(self.inventory):
            if i >= self.max_slots:
                return
            if el is None:
                self.inventory[i] = item
                self.sprite_group.add(item.sprite)
                self.place_sprite_at(item.sprite, i)
                return

    def select_active_item(self, i: Optional[int]) -> None:
        if i is None:
            self.active_item = None
            self.frame.select(None)
            return
        if i < len(self.inventory):
            self.active_item = self.inventory[i]
            self.frame.select(i)

    def extend_twice(self):
        self.inventory = self.inventory[:] + [None] * len(self.inventory)
        self.max_slots *= 2

    def place_sprite_at(self, sprite, i):
        sprite.rect.topleft = ((i + 2) * 50 + 25, 25)
        sprite.image.set_alpha(255)


class Item(abc.ABC):
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.sprite = self.get_sprite()

    @abc.abstractmethod
    def get_sprite(self):
        pass


class Weapon(Item):
    def __init__(self, name, description, ap, range, damage):
        super().__init__(name, description)
        self.ap = ap
        self.range = range
        self.damage = damage


class Consumable(Item):
    @abc.abstractmethod
    def consume(self, player: "Player"):
        pass

    class ConsumableSprite(pygame.sprite.Sprite):
        def __init__(self, img_path):
            super().__init__()
            self.image = pygame.image.load(sprites.img_folder / img_path).convert()
            self.image.set_alpha(0)
            self.image.set_colorkey((0, 0, 0))
            self.rect = self.image.get_rect()
            self.surf = pygame.Surface((50, 50))

    @staticmethod
    def create_sprite_from_pic(img_path):
        return Consumable.ConsumableSprite(img_path)


class WhiteMonster(Consumable):
    def __init__(self):
        super().__init__(name="White Monster", description="Doubles your maximum amount of action points")

    def consume(self, player: "Player"):
        player.ap.max *= 2
        print(player.ap.max)
        player.inventory.remove(self)

    def get_sprite(self):
        return self.create_sprite_from_pic("white_monster.png")


class BlackMonster(Consumable):
    def __init__(self):
        super().__init__(name="Black Monster", description="Restores your action points")

    def consume(self, player: "Player"):
        player.ap.reset_ap(player.ap.max)
        player.inventory.remove(self)

    def get_sprite(self):
        return self.create_sprite_from_pic("black_monster.png")
