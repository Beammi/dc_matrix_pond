import random
import time
from collections import defaultdict
from typing import Callable, DefaultDict, Dict, List

import pygame

import consts
from FishData import FishData
from vivisystem.models import VivisystemFish

# example: "./assets/images/sprites/<pond-name>/"
POND_ASSETS_PATH = "./assets/images/sprites"

# define list of ponds assets
available_pond_assets = {"local-pond", "local-pond-agent", "foreign-pond", "mega-pond", "doo-pond", "khor-pond", "aquagang"}
agent_path = "local-pond-agent"
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

SCREEN_WIDTH = 1180
SCREEN_HEIGHT = 300


class Fish(pygame.sprite.Sprite):
    def __init__(
        self, pos_x=None, pos_y=None, genesis="matrix-pond", parent=None, data: FishData = None
    ):
        super().__init__()
        self.fishData = data or FishData(genesis, parentId=parent)

        # swimming controller
        self.direction = "RIGHT"
        self.face = 1
        self.sprites = []  # Main sprite
        self.leftSprite = []
        self.rightSprite = []
        self.loadSprite()

        self.image = self.sprites[self.current_sprite]
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.topleft = [self.fishData.x, self.fishData.y]
        self.rect.left = self.fishData.x
        self.rect.top = self.fishData.y
        self.rect.right = self.fishData.x + 100
        self.attack_animation = True
        self.current_sprite = 0
        self.rect = self.image.get_rect()
        self.rect.topleft = [self.fishData.x, self.fishData.y]
        self.in_pond_sec = 0
        self.gaveBirth = False
        self.speed = float(random.randrange(5, 20)) / 100

        self.timer = 0
        self.speed_x = 2
        self.speed_y = 1
        self.change_dir_timer = random.randint(60, 180)
        self.add_bullet = None

    @classmethod
    def fromVivisystemFish(cls, fish: VivisystemFish):
        fish_data = FishData(
            fish.genesis,
            fish.lifetime,
            fish.parent_id,
            fish.crowd_threshold,
            fish.pheromone_threshold,
        )
        return cls(data=fish_data)

    def toVivisystemFish(self) -> VivisystemFish:
        return VivisystemFish(
            fish_id=self.getId(),
            parent_id=self.fishData.getId(),
            genesis=self.fishData.getGenesis(),
            crowd_threshold=self.getCrowdThresh(),
            pheromone_threshold=self.fishData.pheromoneThresh,
            lifetime=self.getLifetime(),
        )

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

    def set_is_agent(self, is_agent):
        self.fishData.is_agent = is_agent
        if is_agent:
            self.loadSprite()

    def is_agent(self) -> bool:
        return self.fishData.is_agent

    def flipSprite(self):

        if self.face == 1:
            self.sprites = self.rightSprite
        elif self.face == -1:
            self.sprites = self.leftSprite

        self.current_sprite = 0

    def loadSprite(self):
        path = "local-pond"
        if (
            self.fishData.genesis != "matrix-pond"
            and self.fishData.genesis not in available_pond_assets
        ):
            path = "foreign-pond"
        elif self.fishData.genesis in available_pond_assets:
            path = self.fishData.genesis

        if self.fishData.is_agent:
            path = agent_path

        self.sprites = pond_sprites_container[path][0]
        self.leftSprite = pond_sprites_container[path][1]
        self.rightSprite = pond_sprites_container[path][0]
        self.current_sprite = 0

    def update_ani(self):
        if self.attack_animation:
            self.current_sprite += self.speed  # not correct
            if int(self.current_sprite) >= len(self.sprites):
                self.current_sprite = 0
        self.image = self.sprites[int(self.current_sprite)]

    def move(self):
        self.timer += 1
        if self.timer >= 60:  # Change direction every 60 frames (1 second)
            self.timer = 0
            self.face = random.choice([-1, 1])
            self.speed_x = random.randint(1, 5) * self.face
            self.speed_y = random.randint(-2, 2)
            self.flipSprite()

        if self.timer >= 10 and (self.fishData.is_agent and self.add_bullet):
            x = self.rect.x + 5 if self.face == -1 else self.rect.x + 85
            self.add_bullet(x, self.rect.y + 75, self.face)

        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.face = -self.face
            self.speed_x = -self.speed_x
            self.flipSprite()

        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.speed_y = -self.speed_y

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        self.update_ani()

    def update(self):
        self.move()

    def increasePheromone(self, n):
        self.fishData.pheromone += n
        # TODO: update redis?

    def migrate(self):
        pass

    def getId(self):
        return self.fishData.id

    def getLifetime(self):
        return self.fishData.lifetime

    def isPregnant(self, current_pheromone):
        if current_pheromone < self.fishData.pheromoneThresh:
            return False
        self.fishData.pheromoneThresh += self.fishData.pheromoneThresh
        return True

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

    def set_add_bullet_func(self, func):
        self.add_bullet = func

class FishGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        # self.fishes['matrix-pond']['113230'] = {Fish1, Fish2, ...}
        self.fishes: DefaultDict[str, Dict[str, Fish]] = defaultdict(dict)
        self.percentage: Dict[str, float] = {}
        self.limit = consts.FISHES_DISPLAY_LIMIT
        self.last_updated_time = time.time()

        # self.population_history['matrix-pond'] = [(timestamp, count), ...]
        self.population_history: DefaultDict[str, List[List[tuple]]] = defaultdict(list)

    def add_fish(self, fish: Fish):
        self.fishes[fish.getGenesis()][fish.getId()] = fish
        self.update_percentages()
        if self.get_total() < self.limit:
            self.add(fish)

    def remove_fish(self, genesis, fish_id):
        if genesis in self.fishes:
            self.fishes[genesis].pop(fish_id, None)
            self.update_percentages()

    def update_fishes(self, update: Callable[[Fish], None]):
        for genesis in list(self.fishes.keys()):
            for fish in list(self.fishes[genesis].values()):
                update(fish)

    def get_total(self) -> int:
        return sum([len(self.fishes[key]) for key in self.fishes.keys()])

    def get_percentages(self) -> Dict[str, float]:
        return self.percentage

    def update_percentages(self):
        for genesis in self.fishes.keys():
            total = self.get_total()
            self.percentage[genesis] = len(self.fishes[genesis]) / total if total > 0 else 0

    def update_population_history(self, current_time):
        if current_time - self.last_updated_time <= 2:
            return
        for genesis in self.fishes.keys():
            self.population_history[genesis].append((current_time, len(self.fishes[genesis])))
        self.last_updated_time = current_time

    def get_population_history(self):
        return self.population_history

    def update_display(self):
        current_time = time.time()
        self.update_population_history(current_time)

        self.last_update_time = current_time

        total_fishes = self.get_total()
        if total_fishes > self.limit:
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

    def getFishes(self):
        fishes = []
        for fish in self.fishes["matrix-pond"].values():
            fishes.append(fish)
        return fishes
