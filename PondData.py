class PondData:
    def __init__(self, pondName):
        self.pondName = pondName
        self.fishes = {}

    def __str__(self):
        fishId = ""
        for f in self.fishes.values():
            fishId += f.getId() + " "
            print(f)
        return self.pondName + " " + str(len(self.fishes))

    def getPondName(self):
        return self.pondName

    def getPopulation(self):
        return len(self.fishes)

    def addFish(self, fishData):
        if fishData.id in self.fishes:
            return
        self.fishes[fishData.id] = fishData

    def getFishById(self, fishId):
        return self.fishes.get(fishId)

    def setFish(self, newFishData):
        self.fishes[newFishData.id] = newFishData

    def removeFish(self, fishId):
        self.fishes.pop(fishId, None)
