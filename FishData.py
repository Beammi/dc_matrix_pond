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
    def __init__(self, genesis, parentId=None):
        self.id = randId()
        self.state = "in-pond"
        self.status = "alive"
        self.genesis = genesis  ## Pond name
        self.crowdThreshold = randCrowdThresh()
        self.pheromone = 0
        self.pheromoneThresh = randPheromoneThresh()
        self.lifetime = 60
        self.parentId = parentId
        self.x, self.y = random.randint(50, 650), random.randint(50, 650)
        self.timestamp = datetime.datetime.now()

    def has_time_passed(self, seconds: int) -> bool:
        current_time = datetime.datetime.now()
        time_diff = current_time - self.timestamp
        print(f"elapsed: {time_diff.total_seconds()}")
        print(f"lifetime: {seconds} id: {self.getId()}")
        return time_diff.total_seconds() >= seconds

    def get_remaining_lifetime(self):
        pass

    def getId(self):
        return self.id

    def getState(self):
        return self.state

    def getStatus(self):
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
        if self.parentId:
            return (
                self.id
                + " Genesis: "
                + self.genesis
                + " Parent: "
                + self.parentId
                + " Lifetime: "
                + str(self.lifetime)
            )
        else:
            return self.id + " Genesis: " + self.genesis + " Lifetime: " + str(self.lifetime)
