import datetime
import math
import random


def randId():
    digits = [i for i in range(0, 10)]
    random_str = ""
    for i in range(6):
        index = math.floor(random.random() * 10)
        random_str += str(digits[index])
    return random_str


def randCrowdThresh():
    return random.randint(5, 20)


def randPheromoneThresh():
    return random.randint(30, 60)


class FishData:
    def __init__(
        self, genesis, lifetime=None, parentId=None, crowdThreshold=None, pheromoneThreshold=None
    ):
        self.id = randId()
        self.state = "in-pond"
        self.status = "alive"
        self.genesis = genesis  # Pond name
        self.crowdThreshold = crowdThreshold or randCrowdThresh()
        self.pheromone = 0
        self.pheromoneThresh = pheromoneThreshold or randPheromoneThresh()
        self.lifetime = lifetime or 60
        self.parentId = parentId or randId()
        self.x, self.y = random.randint(50, 650), random.randint(50, 650)
        self.is_agent = False
        self.timestamp = datetime.datetime.now()

    def random_pos(self):
        self.x, self.y = random.randint(50, 650), random.randint(50, 650)

    def has_time_passed(self, seconds: int) -> bool:
        current_time = datetime.datetime.now()
        time_diff = current_time - self.timestamp
        return time_diff.total_seconds() >= seconds

    def getLifeTimeLeft(self):
        current_time = datetime.datetime.now()
        time_diff = current_time - self.timestamp
        return self.lifetime - time_diff.seconds

    def getId(self):
        return self.id

    def getState(self):
        return self.state

    def getStatus(self):
        if self.getLifeTimeLeft == 0:
            self.status = "dead"
        return self.status

    def getGenesis(self):
        return self.genesis

    def getcrowdThreshold(self):
        return self.crowdThreshold

    def pheromone(self):
        return self.pheromone

    def pheromoneThresh(self):
        return self.pheromoneThresh

    def getLifetime(self):
        return self.lifetime

    def parentId(self):
        return self.parentId

    def __str__(self):
        pass
        # if self.parentId:
        #     return (
        #         self.id
        #         + " Genesis: "
        #         + self.genesis
        #         + " Parent: "
        #         + self.parentId
        #         + " Lifetime: "
        #         + str(self.lifetime)
        #     )
        # else:
        #     return self.id + " Genesis: " + self.genesis + " Lifetime: " + str(self.lifetime)
