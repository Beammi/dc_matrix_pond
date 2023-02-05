import random
from collections import defaultdict
from typing import Callable, DefaultDict, Dict

import pygame

from FishData import FishData

# example: "./assets/images/sprites/<pond-name>/"
POND_ASSETS_PATH = "./assets/images/sprites"

# define list of ponds assets
available_pond_assets = {"local-pond", "foreign-pond"}
# pond_path: ([left sprites], [right sprites])
pond_sprites_container = {p: ([], []) for p in available_pond_assets}


def load_sprites_right(pond_name):
    path = f"{POND_ASSETS_PATH}/{pond_name}/"
    for i in range(1, 5):
        fish_path = path + str(i) + ".png"
        img = pygame.image.load(str(fish_path))
        img = pygame.transform.scale(img, (100, 100))
        img = pygame.transform.flip(img, True, False)
        pond_sprites_container[pond_name][0].append(img)


def load_sprites_left(pond_name):
    path = f"{POND_ASSETS_PATH}/{pond_name}/"
    for i in range(1, 5):
        fish_path = path + str(i) + ".png"
        img = pygame.image.load(fish_path)
        img = pygame.transform.scale(img, (100, 100))
        pond_sprites_container[pond_name][1].append(img)


def load_sprites():
    for pond in available_pond_assets:
        load_sprites_left(pond)
        load_sprites_right(pond)


load_sprites()


class Fish(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, genesis="matrix-fish", parent=None, data: FishData = None):
        super().__init__()
        self.fishData = FishData(genesis, parent) if not data else data

        # swimming controller
        self.direction = "RIGHT"
        self.face = 1
        self.attack_animation = False
        self.sprites = []  # Main sprite
        self.leftSprite = []
        self.rightSprite = []
        self.loadSprite()

        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.topleft = [self.fishData.x, self.fishData.y]
        self.rect.left = self.fishData.x
        self.rect.top = self.fishData.y
        self.rect.right = pos_x + 100
        self.attack_animation = True
        self.current_sprite = 0
        self.rect = self.image.get_rect()
        self.rect.topleft = [self.fishData.x, self.fishData.y]
        self.in_pond_sec = 0
        self.gaveBirth = False
        self.speed = float(random.randrange(5, 20)) / 100

    def getFishData(self):
        return self.fishData

    def getFishTLPos(self):
        return self.rect.topleft

    def getFishx(self):
        return self.rect.left

    def getFishy(self):
        return self.rect.top

    def die(self):
        self.kill()

    def flipSprite(self):

        if self.face == 1:
            self.sprites = self.rightSprite
        elif self.face == -1:
            self.sprites = self.leftSprite

        self.current_sprite = 0

    def loadSprite(self):
        path = "local-pond"
        if (
            self.fishData.genesis != "matrix-fish"
            and self.fishData.genesis not in available_pond_assets
        ):
            path = "foreign-pond"
        elif self.fishData.genesis in available_pond_assets:
            path = self.fishData.genesis

        self.sprites = pond_sprites_container[path][0]
        self.leftSprite = pond_sprites_container[path][1]
        self.rightSprite = pond_sprites_container[path][0]
        self.current_sprite = 0

    def update_ani(self):
        if self.attack_animation:
            self.current_sprite += self.speed
            if int(self.current_sprite) >= len(self.sprites):
                self.current_sprite = 0
        self.image = self.sprites[int(self.current_sprite)]

    def move(self, speed_x):
        if self.rect.left <= 0:
            self.face = 1
            self.flipSprite()
        elif self.rect.left >= 1180:
            self.face = -1
            self.flipSprite()

        speed_x = random.randint(1, 5) * self.face

        self.rect.x += speed_x
        self.update_ani()

    def update(self):
        self.move(3)

    def increasePheromone(self, n):
        self.fishData.pheromone += n
        # TODO: update redis?

    def migrate(self):
        pass

    def getId(self):
        return self.fishData.id

    def getLifetime(self):
        return self.fishData.lifetime

    def isPregnant(self):
        return self.fishData.pheromone >= self.fishData.pheromoneThresh

    def updateLifeTime(self):
        self.in_pond_sec += 1
        if self.fishData.has_time_passed(self.fishData.lifetime):
            self.fishData.status = "dead"

    def resetPheromone(self):
        self.fishData.pheromone = 0

    def getGenesis(self):
        return self.fishData.genesis

    def getCrowdThresh(self):
        return self.fishData.crowdThreshold

    def giveBirth(self):
        self.gaveBirth = True

    def shouldMigrate(self) -> bool:
        pass


FISHES_DISPLAY_LIMIT = 100
import time


class FishGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        # self.fishes['matrix-fish']['113230'] = {Fish1, Fish2, ...}
        self.fishes: DefaultDict[str, Dict[str, Fish]] = defaultdict(dict)
        self.percentage: Dict[str, float] = {}
        self.limit = FISHES_DISPLAY_LIMIT
        self.last_update_time = time.time()

    def add_fish(self, fish: Fish):
        self.fishes[fish.getGenesis()][fish.getId()] = fish
        if self.get_total() < self.limit:
            self.add(fish)

    def remove_fish(self, genesis, fish_id):
        if genesis in self.fishes:
            fish = self.fishes[genesis].pop(fish_id, None)
            if fish:
                self.remove(fish)

    def update_fishes(self, update: Callable[[Fish], None]):
        for genesis in list(self.fishes.keys()):
            for fish in list(self.fishes[genesis].values()):
                update(fish)

    def get_total(self) -> int:
        return sum([len(self.fishes[key]) for key in self.fishes.keys()])

    def get_percentages(self) -> Dict[str, float]:
        return self.percentage

    def update_display(self):
        current_time = time.time()
        self.last_update_time = current_time

        total_fishes = self.get_total()
        if total_fishes > self.limit:
            print("Over limit, re-calculating..")
            for fish_type in self.fishes.keys():
                self.percentage[fish_type] = len(self.fishes[fish_type]) / total_fishes

            self.empty()
            for fish_type in self.fishes.keys():
                fish_type_limit = int(self.percentage[fish_type] * self.limit)
                # if current_time - self.last_update_time < 5:
                #     fish_type_fishes = random.sample(
                #         list(self.fishes[fish_type].values()), fish_type_limit
                #     )
                #     for fish_sprite in fish_type_fishes:
                #         self.add(fish_sprite)
                # else:
                for i, (fish_id, fish_sprite) in enumerate(self.fishes[fish_type].items()):
                    if i < fish_type_limit:
                        self.add(fish_sprite)
                    else:
                        break
        self.update()
