# from turtle import update
import random
import sys
import threading
from random import randint

import pygame
from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from Client import Client

# from run import Dashboard
from dashboard import Dashboard
from Fish import Fish
from FishStore import FishStore
from pondDashboard import PondDashboard
from PondData import PondData


class Pond:
    def __init__(self, fishStore: FishStore):
        pygame.init()
        self.name = "matrix-fish"
        self.moving_sprites = pygame.sprite.Group()
        self.sharkImage = pygame.image.load("./assets/images/sprites/shark.png")
        self.sharkImage = pygame.transform.scale(self.sharkImage, (128, 128))
        self.msg = ""
        self.pondData = PondData(self.name)
        self.network = None
        self.sharkTime = 0
        self.displayShark = False
        self.fishStore: FishStore = fishStore

        # EVENTS
        self.UPDATE_EVENT = pygame.USEREVENT + 1
        self.PHEROMONE_EVENT = pygame.USEREVENT + 2
        self.SHARK_EVENT = pygame.USEREVENT + 3

        self.fishes = self.fishStore.get_fishes()
        for fish in self.fishes.values():
            self.moving_sprites.add(fish)

    def getPondData(self):
        return self.pondData

    def getPopulation(self):
        return len(self.fishes)

    def randomFish(self):
        key = next(iter(self.fishes))
        return self.fishes[key]

    # def sharkAttack(self, screen, fish):
    #     screen.blit(self.sharkImage, (fish.getFishx(), fish.getFishy()))
    #     self.removeFish(fish)
    #     fish.die()

    def spawnFish(self, parentFish=None):
        tempFish = Fish(100, 100, self.name, parentFish.getId())
        self.fishStore.add_fish(tempFish.fishData)
        self.fishes[tempFish.getId()] = tempFish
        self.moving_sprites.add(tempFish)

    def pheromoneCloud(self):
        pheromone = 20
        # RuntimeError: dictionary changed size during iteration
        # need to use .items() instead of .values()
        for f in list(self.fishes.values()):
            f.increasePheromone(pheromone)

            if f.isPregnant():  ## check that pheromone >= pheromone threshold
                newFish = Fish(50, randint(50, 650), f.getGenesis(), f.getId())
                self.fishStore.add_fish(newFish.fishData)
                print("CHILD FISH")
                print("number of fishes:", len(self.fishes))
                self.addFish(newFish)
                # self.pondData.addFish( newFish.fishData)

                f.resetPheromone()

    def migrateFish(self, fishIndex, destination):
        # destination = random.choice(self.network.other_ponds.keys())
        print(
            "---------------------------FISH SHOULD BE REMOVED BY MIGRATE-------------------------"
        )

        temp = self.fishes[fishIndex]
        # self.fishes.pop(fishIndex)
        # self.moving_sprites.remove(temp)
        # self.pondData.migrateFish(temp.getId())
        # self.network.pond = self.pondData
        self.removeFish(temp)
        self.network.migrate_fish(temp.fishData, destination)

    # ---------------implement---------------#``

    def addFish(self, newFishData):  # from another pond
        self.fishes[newFishData.getId()] = newFishData
        self.pondData.addFish(newFishData.fishData)
        self.fishStore.add_fish(newFishData.fishData)
        self.moving_sprites.add(newFishData)
        self.network.pond = self.pondData

    def removeFish(self, fish):
        self.fishes.pop(fish.getId(), None)
        print("---------------------------FISH SHOULD BE REMOVED-------------------------")
        print(fish.getId())
        self.pondData.removeFish(fish.getId())
        self.network.pond = self.pondData
        self.moving_sprites.remove(fish)

    def update(self, injectPheromone=False):
        for fish in list(self.fishes.values()):
            self.update_fish(fish)
        # self.pool.map(self.update_fish, self.fishes)

    def update_fish(self, f: Fish, ind=2, injectPheromone=False):
        f.updateLifeTime()  # decrease life time by 1 sec
        if f.fishData.status == "dead":
            self.removeFish(f)
            return
        self.pondData.setFish(f.fishData)

        # Other pond exists
        if len(self.network.other_ponds.keys()) > 0:
            # print( f.getId(), f.in_pond_sec)
            if f.getGenesis() != self.name and f.in_pond_sec >= 5 and not f.gaveBirth:
                newFish = Fish(50, randint(50, 650), f.fishData.genesis, f.fishData.id)
                self.fishStore.add_fish(newFish.fishData)
                newFish.giveBirth()  ## not allow baby fish to breed
                print("ADD FISH MIGRATED IN POND FOR 5 SECS")
                self.addFish(newFish)
                f.giveBirth()

                # self.pondData.addFish( newFish.fishData )
            if f.getGenesis() == self.name and f.in_pond_sec <= 15:
                if random.getrandbits(1):
                    # print('OTHER POND >>> ',self.network.other_ponds.keys())
                    dest = random.choice(list(self.network.other_ponds.keys()))
                    self.migrateFish(ind, dest)
                    # self.network.migrate_fish(f, dest)
                    # self.pondData.migrateFish(f.getId())
                    parent = None
                    if f.fishData.parentId:
                        parent = f.fishData.parentId
                    for ind2, f2 in enumerate(self.fishes.values()):
                        if (
                            parent
                            and f2.fishData.parentId == parent
                            or f2.fishData.parentId == f.getId()
                        ):
                            self.migrateFish(ind2, dest)
                            # self.network.migrate_fish( f2, dest)
                            # self.pondData.migrateFish(f2.getId())
                            break

            elif f.getGenesis() == self.name and f.in_pond_sec >= 15:
                dest = random.choice(list(self.network.other_ponds.keys()))
                self.migrateFish(ind, dest)
                # self.network.migrate_fish(f, dest)
                # self.pondData.migrateFish(f.getId())
                parent = None
                if f.fishData.parentId:
                    parent = f.fishData.parentId
                for ind2, f2 in enumerate(self.fishes.values()):
                    if (
                        parent
                        and f2.fishData.parentId == parent
                        or f2.fishData.parentId == f.getId()
                    ):
                        self.migrateFish(ind2, dest)
                        # self.network.migrate_fish( f2, dest)
                        # self.pondData.migrateFish(f2.getId())
                        break
            else:
                dest = random.choice(list(self.network.other_ponds.keys()))
                if self.getPopulation() > f.getCrowdThresh():

                    self.migrateFish(ind, dest)
                    # self.network.migrate_fish(f, dest )
                    # self.pondData.migrateFish( f.fishData.id )
                    return

        if injectPheromone:
            self.pheromoneCloud()
        # print("Client send :",self.pondData)
        self.network.pond = self.pondData

    def run(self):
        # General setup
        direction = 1
        speed_x = 3
        # speed_y = 4
        random.seed(123)

        self.network = Client(self.pondData)
        # self.msg = self.network.get_msg()
        msg_handler = threading.Thread(target=self.network.get_msg)
        msg_handler.start()
        send_handler = threading.Thread(target=self.network.send_pond)
        send_handler.start()
        lifetime_handler = threading.Thread(target=self.network.handle_lifetime)
        lifetime_handler.start()

        pygame.init()
        screen = pygame.display.set_mode((1280, 720))

        bg = pygame.image.load("./assets/images/background/bg.jpg")
        bg = pygame.transform.scale(bg, (1280, 720))
        pygame.display.set_caption("Fish Haven Project")
        clock = pygame.time.Clock()
        start_time = pygame.time.get_ticks()
        pregnant_time = pygame.time.get_ticks()

        begin_fish = Fish(10, 100)
        self.addFish(begin_fish)
        self.fishStore.add_fish(begin_fish.fishData)

        # self.addFish(Fish(10,140, genesis="peem"))
        # self.addFish(Fish(100,200, genesis="dang"))

        app = QApplication(sys.argv)
        other_pond_list = []

        running = True
        pygame.time.set_timer(self.UPDATE_EVENT, 1000)
        pygame.time.set_timer(self.PHEROMONE_EVENT, 5000)
        pygame.time.set_timer(self.SHARK_EVENT, 15000)

        while running:
            #   if len(self.fishes) > 100000:
            #      while len(self.fishes) > 100000:
            #         self.removeFish(self.randomFish())
            # self.fishes[kill].die()

            # print(self.network.get_msg())
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # cleanup
                    running = False
                    pygame.time.set_timer(self.UPDATE_EVENT, 0)
                    pygame.time.set_timer(self.PHEROMONE_EVENT, 0)
                    pygame.time.set_timer(self.SHARK_EVENT, 0)
                    self.network.disconnect()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        # print(self.fishes[0].getId())
                        allPondsNum = len(self.fishes)
                        for p in self.network.other_ponds.values():
                            allPondsNum += p.getPopulation()
                        d = Dashboard(list(self.fishes.values()), allPondsNum)
                        pond_handler = threading.Thread(target=app.exec_)
                        pond_handler.start()
                    elif event.key == pygame.K_LEFT:
                        for pondName in list(self.network.other_ponds.keys()):
                            other_pond_list.append(self.network.other_ponds.get(pondName))
                        pd = PondDashboard(other_pond_list)
                        pond_handler = threading.Thread(target=app.exec_)
                        pond_handler.start()
                elif event.type == self.UPDATE_EVENT:
                    self.update()
                elif event.type == self.PHEROMONE_EVENT:
                    # pregnant_time?
                    self.pheromoneCloud()
                elif event.type == self.SHARK_EVENT:
                    if len(self.fishes) > 4:
                        deadFish = self.randomFish()
                        screen.blit(
                            self.sharkImage, (deadFish.getFishx() + 30, deadFish.getFishy())
                        )
                        pygame.display.flip()
                        pygame.event.pump()
                        pygame.time.delay(500)
                        self.removeFish(deadFish)
                        deadFish.die()
                        start_time = pygame.time.get_ticks()

            other_pond_list = []

            # print("POND:"+self.msg.__str__())
            # print("pond: ", self.pondData)
            # self.msg = self.network.send_pond()
            # print(self.msg.data)
            if len(self.network.messageQ) > 0:
                self.msg = self.network.messageQ.pop()
                if self.msg.action == "MIGRATE":
                    newFish = Fish(
                        50,
                        randint(50, 650),
                        self.msg.data["fish"].genesis,
                        self.msg.data["fish"].parentId,
                    )
                    print("ADD MIGRATED FISH")
                    self.addFish(newFish)

                    # self.pondData.addFish(newFish.fishData)
                    # self.network.pond = self.pondData

            screen.fill((0, 0, 0))
            screen.blit(bg, [0, 0])

            self.moving_sprites.update(screen=screen)

            # print(len(self.fishes))

            # if time_since_last_data_send > 2000:
            #     pass
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()
