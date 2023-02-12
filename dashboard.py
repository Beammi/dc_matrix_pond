import time
from typing import DefaultDict, Dict

from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QGroupBox,
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

from Fish import FishGroup
from fishFrame import FishFrame


class Dashboard(QMainWindow):
    def __init__(self, fishes: FishGroup):
        super().__init__()
        self.fishes: FishGroup = fishes
        self.last_updated = time.time()
        self.label = QLabel(self)
        self.update_dashboard()
        self.initUI()

    def update_dashboard(self):
        current_time = time.time()
        if current_time - self.last_updated < 2:
            return
        percentages = self.fishes.get_percentages()
        percentages_str = ""
        for genesis, p in percentages.items():
            percentages_str += f"{genesis}: {p * 100:.2f}%\n"
        self.label.setText(
            "Vivi Population : " + str(self.fishes.get_total()) + "\n" + percentages_str
        )

    def initUI(self):

        self.scroll = (
            QScrollArea()
        )  # Scroll Area which contains the widgets, set as the centralWidget

        self.widget = QWidget()  # Widget that contains the collection of Vertical Box

        self.vbox = (
            QVBoxLayout()
        )  # The Vertical Box that contains the Horizontal Boxes of  labels and buttons

        self.grid = QGridLayout()

        # temp = ["Fish ID: 123", "State: In Pond", "Status: alive", "Genesis: matrix-fish", "Crowd Threshold: 5/10", "Pheromone Level: 4/5", "Lifetime: 30/60"]

        # print(self.fished[0].getFishData().getGenesis())

        num = len(self.fishes)

        j = 0

        temp = 0

        i = 0

        font = self.label.font()

        font.setPointSize(30)

        font.setBold(True)

        self.label.setFont(font)

        # for r in range(0, num):

            # print("out", i, temp, j)

        #     while j < 2 and i < num:

        #         # print("here", i, temp, j)

        #     # info = [
        #     #         self.fishes[key].getFishData().getId(),
        #     #         self.fishes[key].getFishData().getState(),
        #     #         self.fishes[key].getFishData().getStatus(),
        #     #         self.fishes[key].getFishData().getGenesis(),
        #     #         str(self.fishes[key].getFishData().lifetime),
        #     # ]
        #     info = self.fishes.getFishes()

        #     self.grid.addWidget(FishFrame(info, self.widget), temp, j)

        #     i += 1

        #     j += 1

        #     j = 0

        #     temp += 1

        self.vbox.addWidget(self.label)

        self.vbox.addLayout(self.grid)

        self.widget.setLayout(self.vbox)

        # Scroll Area Properties

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.scroll.setWidgetResizable(True)

        self.scroll.setWidget(self.widget)

        self.setCentralWidget(self.scroll)

        self.setGeometry(0, 290, 500, 700)

        self.setWindowTitle("Pond Dashboard")

        self.show()

        return

    def update(fishes):

        pass
