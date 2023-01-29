from FishData import FishData
from PondData import PondData


class Payload:
    def __init__(self, action="", data=object):
        self.action = action
        self.data = data
