# from turtle import update
import random
import sys
import threading
from random import choice, randint
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

# from run import Dashboard
from dashboard import Dashboard
from Fish import Fish, FishGroup
from FishData import FishData
from FishStore import FishStore
from pondDashboard import PondDashboard
from vivisystem.client import VivisystemClient
from vivisystem.models import EventType, VivisystemFish, VivisystemPond
import consts

blue_pill_img = pygame.image.load("./assets/images/sprites/blue-pill.png")
blue_pill_img = pygame.transform.scale(blue_pill_img, (15, 30))

red_pill_img = pygame.image.load("./assets/images/sprites/red-pill.png")
red_pill_img = pygame.transform.scale(red_pill_img, (15, 30))

class Pill(pygame.sprite.Sprite):
	def __init__(self, color, x, y):
		super().__init__()
		self.color = color
		self.image = blue_pill_img if color == "blue" else red_pill_img
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

	def update(self):
		self.rect.y += 5
		if self.rect.y > 720:
			self.kill()
	
class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		super().__init__()
		self.image = pygame.Surface([5, 3])
		self.image.fill("red")
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.direction = direction

	def update(self):
		self.rect.x += 5 * self.direction
		if self.rect.x >= consts.SCREEN_WIDTH or self.rect.x < 0:
			self.kill()


class Pond:
	def __init__(self, fishStore: FishStore, vivi_client: VivisystemClient, name="matrix-pond"):
		pygame.init()
		self.name = name
		self.fish_group = FishGroup()
		self.bullet_group = pygame.sprite.Group()
		self.sharkImage = pygame.image.load("./assets/images/sprites/shark.png")
		self.sharkImage = pygame.transform.scale(self.sharkImage, (128, 128))
		self.sharkTime = 0
		self.displayShark = False
		self.vivi_client = vivi_client
		self.connected_ponds = {}
		self.fishStore: FishStore = fishStore
		self.pheromone = self.fishStore.get_pheromone()

		# EVENTS
		self.UPDATE_EVENT = pygame.USEREVENT + 1
		self.PHEROMONE_EVENT = pygame.USEREVENT + 2
		self.SPAWN_FISH_EVENT = pygame.USEREVENT + 3
		self.SEND_STATUS_EVENT = pygame.USEREVENT + 4
		self.PILL_EVENT = pygame.USEREVENT + 5

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
		tempFish = Fish(100, 100, self.name, parentFish.getId() if parentFish else "-")
		self.fishStore.add_fish(tempFish.fishData)
		self.fish_group.add_fish(tempFish)

	def pheromoneCloud(self):
		if self.fish_group.get_total() > consts.FISHES_POND_LIMIT:
			return

		# TODO: increase this rate over time?
		self.pheromone += randint(20, 50) * consts.BIRTH_RATE
		self.fishStore.set_pheromone(self.pheromone)

	def addFish(self, fish: Fish):  # from another pond
		# self.pondData.addFish(newFishData.fishData)
		self.fishStore.add_fish(fish.fishData)
		self.fish_group.add_fish(fish)

	def removeFish(self, fish: Fish):
		print("---------------------------FISH SHOULD BE REMOVED-------------------------")
		print(fish.getId())
		self.fish_group.remove_fish(fish.getGenesis(), fish.getId())
		fish.die()

	def update(self, injectPheromone=False):
		self.fish_group.update_fishes(self.update_fish)
		self.fishStore.set_pheromone(self.pheromone)

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

		# Other pond exists
		if self.connected_ponds:
			# print( f.getId(), f.in_pond_sec)
			if f.getGenesis() != self.name and f.in_pond_sec >= 5 and not f.gaveBirth:
				newFish = Fish(50, randint(50, 650), f.fishData.genesis, f.fishData.id)
				self.addFish(newFish)
				newFish.giveBirth()  # not allow baby fish to breed
				print("ADD FISH MIGRATED IN POND FOR 5 SECS")
				f.giveBirth()

			if f.getGenesis() == self.name and f.in_pond_sec <= 15:
				pass
			elif f.getGenesis() == self.name and f.in_pond_sec >= 15:
				if self.connected_ponds:
					random_pond = random.choice(list(self.connected_ponds))
					self.vivi_client.migrate_fish(random_pond, f.toVivisystemFish())
					self.removeFish(f)
			else:
				if self.getPopulation() > f.getCrowdThresh():
					random_pond = random.choice(list(self.connected_ponds))
					self.vivi_client.migrate_fish(random_pond, f.toVivisystemFish())
					self.removeFish(f)

		if injectPheromone:
			self.pheromoneCloud()

	def handle_migrate(self, fish: VivisystemFish):
		fish = Fish.fromVivisystemFish(fish)
		self.addFish(fish)

	def handle_status(self, pond: VivisystemPond):
		self.connected_ponds[pond.name] = pond

	def handle_disconnect(self, pond_name: str):
		if pond_name in self.connected_ponds:
			del self.connected_ponds[pond_name]
			print(pond_name, "Disconnected")

	def add_bullet(self, start_x, start_y, direction):
		bullet = Bullet(start_x, start_y, direction)
		self.bullet_group.add(bullet)

	def run(self):
		mapHandler = {
			EventType.MIGRATE: self.handle_migrate,
			EventType.STATUS: self.handle_status,
			EventType.DISCONNECT: self.handle_disconnect,
		}
		for event, handler in mapHandler.items():
			self.vivi_client.handle_event(event, handler)

		# General setup
		direction = 1
		speed_x = 3
		# speed_y = 4
		# random.seed(123)

		dashboard: Union[None, Dashboard] = None
		vivisystem_dashboard: Union[None, PondDashboard] = None

		# lifetime_handler = threading.Thread(target=self.network.handle_lifetime)
		# lifetime_handler.start()

		pygame.init()
		screen = pygame.display.set_mode((1280, 720))

		bg = pygame.image.load("./assets/images/background/bg.jpg")
		bg = pygame.transform.scale(bg, (1280, 720))
		pygame.display.set_caption(f"Fish Haven Project: {self.name} Pond")
		clock = pygame.time.Clock()
		start_time = pygame.time.get_ticks()
		pregnant_time = pygame.time.get_ticks()

		self.spawnFish()

		app = QApplication(sys.argv)

		pill_group = pygame.sprite.Group()


		running = True
		pygame.time.set_timer(self.UPDATE_EVENT, 1000)
		pygame.time.set_timer(self.SPAWN_FISH_EVENT, 3000)  # spawn local fish
		pygame.time.set_timer(self.SEND_STATUS_EVENT, 2000)
		pygame.time.set_timer(self.PILL_EVENT, 3000)
		pygame.time.set_timer(self.PHEROMONE_EVENT, 15000)

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
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_RIGHT:
						# print(self.fishes[0].getId())
						dashboard = Dashboard(self.fish_group)
						pond_handler = threading.Thread(target=app.exec_)
						pond_handler.start()
					elif event.key == pygame.K_LEFT:
						vivisystem_dashboard = PondDashboard(self.connected_ponds)
						pond_handler = threading.Thread(target=app.exec_)
						pond_handler.start()
				elif event.type == self.UPDATE_EVENT:
					self.update()
				elif event.type == self.PHEROMONE_EVENT:
					# pregnant_time?
					self.pheromoneCloud()
				elif event.type == self.PILL_EVENT:
					pill_color = random.choice(["blue", "red"])
					pill_x = random.randint(0, screen.get_width() - 20)
					pill = Pill(pill_color, pill_x, 0)
					pill_group.add(pill)
				elif event.type == self.SEND_STATUS_EVENT:
					self.vivi_client.send_status(
						VivisystemPond(
							name=self.name,
							pheromone=self.pheromone,
							total_fishes=self.getPopulation(),
						)
					)
				elif event.type == self.SPAWN_FISH_EVENT:
					self.spawnFish()

			if dashboard:
				dashboard.update_dashboard(self.pheromone)
			if vivisystem_dashboard:
				vivisystem_dashboard.update_dashboard()

			self.fish_group.update_display()
			pill_group.update()
			self.bullet_group.update()

			screen.fill((0, 0, 0))
			screen.blit(bg, [0, 0])

			pill_fish_collisions = pygame.sprite.groupcollide(
				pill_group, self.fish_group, False, False
			)
			for pill, fish_list in pill_fish_collisions.items():
				for fish in fish_list:
					if pill.color == "red":
						self.removeFish(fish)
					else:
						print("set fish to agent")
						fish.set_is_agent(True)
						fish.set_add_bullet_func(self.add_bullet)

					pill.kill()

			bullet_fish_collisions = pygame.sprite.groupcollide(
				self.bullet_group, self.fish_group, False, False
			)
			for bullet, fish_list in bullet_fish_collisions.items():
				for fish in fish_list:
					if not fish.is_agent():
						self.removeFish(fish)
						bullet.kill()

			self.fish_group.draw(screen)
			pill_group.draw(screen)
			self.bullet_group.draw(screen)

			pygame.display.flip()
			clock.tick(60)

		pygame.quit()
		sys.exit()
