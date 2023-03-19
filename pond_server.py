# from turtle import update
import random
import sys
import threading
from random import randint
from typing import Union

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

import consts
from Client import Client

# from run import Dashboard
from dashboard import Dashboard
from Fish import Fish, FishGroup
from FishData import FishData
from FishStore import FishStore
from pondDashboard import PondDashboard
from PondData import PondData


class Pond:
    def __init__(self, fishStore: FishStore, name="matrix-fish"):
        pygame.init()
        self.name = name
        self.fish_group = FishGroup()
        self.pondData = PondData(self.name)
        self.network = None
        self.sharkTime = 0
        self.displayShark = False
        self.fishStore: FishStore = fishStore
        self.pheromone = self.fishStore.get_pheromone()

        # EVENTS
        self.UPDATE_EVENT = pygame.USEREVENT + 1
        self.PHEROMONE_EVENT = pygame.USEREVENT + 2
        for fish in self.fishStore.get_fishes().values():
            self.fish_group.add_fish(fish)
        self.fish_group.update_display()

    def getPondData(self):
        return self.pondData

    def getPopulation(self):
        return self.fish_group.get_total()

    def randomFish(self):
        key = next(iter(self.fishes))
        return self.fishes[key]

    def spawnFish(self, parentFish: Fish = None):
        tempFish = Fish(100, 100, self.name, parentFish.getId()
                        if parentFish else "-")
        self.fishStore.add_fish(tempFish.fishData)
        self.fish_group.add_fish(tempFish)

    def pheromoneCloud(self):
        if self.fish_group.get_total() > consts.FISHES_POND_LIMIT:
            return

        # TODO: increase this rate over time?
        self.pheromone += randint(20, 50) * consts.BIRTH_RATE
        self.fishStore.set_pheromone(self.pheromone)

    def addFish(self, fish: Fish):  # from another pond
        self.fishStore.add_fish(fish.fishData)
        self.fish_group.add_fish(fish)
        self.network.pond = self.pondData

    def removeFish(self, fish: Fish):
        self.pondData.removeFish(fish.getId())
        self.network.pond = self.pondData
        self.fish_group.remove_fish(fish.getGenesis(), fish.getId())

    def update(self, injectPheromone=False):
        self.fish_group.update_fishes(self.update_fish)
        self.fishStore.set_pheromone(self.pheromone)
        print(self.getPopulation())
        print("pheromone", self.pheromone)

    # will apply to indiviual fish
    def update_fish(self, f: Fish, injectPheromone=False):
        f.updateLifeTime()  # decrease life time by 1 sec
        if f.fishData.status == "dead":
            self.removeFish(f)
            return

        if f.isPregnant(self.pheromone):  # check that pheromone >= pheromone threshold
            newFish = Fish(50, randint(50, 650), f.getGenesis(), f.getId())
            self.fishStore.add_fish(newFish.fishData)
            self.addFish(newFish)
            # self.pondData.addFish( newFish.fishData)
            self.pheromone -= f.fishData.crowdThreshold // 2

        self.pondData.setFish(f.fishData)

        # Other pond exists
        if len(self.network.other_ponds.keys()) > 0:
            # print( f.getId(), f.in_pond_sec)
            if f.getGenesis() != self.name and f.in_pond_sec >= 5 and not f.gaveBirth:
                newFish = Fish(50, randint(50, 650),
                               f.fishData.genesis, f.fishData.id)
                self.addFish(newFish)
                newFish.giveBirth()  # not allow baby fish to breed
                print("ADD FISH MIGRATED IN POND FOR 5 SECS")
                f.giveBirth()

                # self.pondData.addFish( newFish.fishData )
            if f.getGenesis() == self.name and f.in_pond_sec <= 15:
                if random.getrandbits(1):
                    # print('OTHER POND >>> ',self.network.other_ponds.keys())
                    if self.network.migrate_random(f.fishData):
                        self.removeFish(f)

            elif f.getGenesis() == self.name and f.in_pond_sec >= 15:
                if self.network.migrate_random(f.fishData):
                    self.removeFish(f)
            else:
                if self.getPopulation() > f.getCrowdThresh():
                    if self.network.migrate_random(f.fishData):
                        self.removeFish(f)
                    return

        if injectPheromone:
            self.pheromoneCloud()
        self.network.pond = self.pondData

    def handle_migrate(self, fish_data: FishData):
        fish_data.random_pos()
        fish = Fish(data=fish_data)
        self.addFish(fish)

    def run(self):
        self.network = Client(
            self.pondData, handle_migrate=self.handle_migrate)

        pygame.init()
        clock = pygame.time.Clock()
        start_time = pygame.time.get_ticks()
        pregnant_time = pygame.time.get_ticks()

        self.spawnFish()

        app = QApplication(sys.argv)
        other_pond_list = []

        running = True
        pygame.time.set_timer(self.UPDATE_EVENT, 1000)
        pygame.time.set_timer(self.PHEROMONE_EVENT, 15000)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # cleanup
                    running = False
                    pygame.time.set_timer(self.UPDATE_EVENT, 0)
                    pygame.time.set_timer(self.PHEROMONE_EVENT, 0)
                    self.network.disconnect()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        # print(self.fishes[0].getId())
                        dashboard = Dashboard(self.fish_group)
                        pond_handler = threading.Thread(target=app.exec_)
                        pond_handler.start()
                    elif event.key == pygame.K_LEFT:
                        vivisystem_dashboard = PondDashboard(self.network)
                        pond_handler = threading.Thread(target=app.exec_)
                        pond_handler.start()
                elif event.type == self.UPDATE_EVENT:
                    self.update()
                elif event.type == self.PHEROMONE_EVENT:
                    # pregnant_time?
                    self.pheromoneCloud()

            self.fish_group.update_display()
            clock.tick(60)

        pygame.quit()
        sys.exit()
