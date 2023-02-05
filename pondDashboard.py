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

from Client import Client
from pondFrame import PondFrame


class PondDashboard(QMainWindow):
    def __init__(self, client, allPond=None):
        super().__init__()
        self.client: Client = client
        self.ponds = allPond
        self.label = QLabel(self)
        self.update_dashboard()
        self.initUI()

    def update_dashboard(self):
        self.label.setText(f"Connected ponds: {self.client.other_ponds}")

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
        # print(self.fishe[0].getFishData().getGenesis())
        # num = len(self.fished)
        # num = len(self.ponds)

        # i, j, temp = 0, 0, 0
        # for r in range(0, num):
        #     # print("out", i, temp, j)
        #     while j < 2 and i < num:
        #         # print("here", i, temp, j)
        #         info = [
        #             self.ponds[i].getPondName(),
        #             self.ponds[i].getPopulation(),
        #             self.ponds[i].fishes,
        #         ]
        #         self.grid.addWidget(PondFrame(info, self.widget), temp, j)
        #         i += 1
        #         j += 1
        #     j = 0
        #     temp += 1

        font = self.label.font()
        font.setPointSize(30)
        font.setBold(True)
        self.label.setFont(font)

        self.vbox.addWidget(self.label)
        self.vbox.addLayout(self.grid)
        self.widget.setLayout(self.vbox)

        # Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.setCentralWidget(self.scroll)

        self.setGeometry(0, 20, 800, 200)
        self.setWindowTitle("Vivisystem Dashboard")
        self.show()

        return

    def update(self):
        pass
