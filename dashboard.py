import time
from typing import DefaultDict, Dict

import pyqtgraph as pg
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

import consts
from Fish import FishGroup


class Dashboard(QMainWindow):
    def __init__(self, fishes: FishGroup):
        super().__init__()
        self.fishes: FishGroup = fishes
        self.last_updated = time.time()
        self.label = QLabel(self)
        self.colors = [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
        ]
        self.lines = {}
        self.initUI()

    def update_dashboard(self, pheromone: int):
        current_time = time.time()
        if current_time - self.last_updated < 2:
            return
        self.last_updated = current_time

        percentages = self.fishes.get_percentages()
        percentages_str = ""
        for genesis, p in percentages.items():
            percentages_str += f"{genesis}: {p * 100:.2f}%\n"

        label_str = (
            "Pond Population : " + str(self.fishes.get_total()) + "\n" + percentages_str + "\n"
        )

        label_str += f"Pond Pheremone: {pheromone}\n"

        label_str += f"\nConstants:\n Population Limit: {consts.FISHES_POND_LIMIT}\n"
        label_str += f" Display Limit: {consts.FISHES_DISPLAY_LIMIT}\n"
        label_str += f" Birth Rate: {consts.BIRTH_RATE}x\n"

        self.label.setText(label_str)
        self.update_history_graph()

    def update_history_graph(self):
        population_history = self.fishes.get_population_history()

        for i, (key, data) in enumerate(population_history.items()):
            x = [d[0] for d in data]
            y = [d[1] for d in data]

            if key not in self.lines:
                color = self.colors[i % len(self.colors)]
                symbol_pen = QtGui.QPen(QtGui.QColor(*color))
                symbol_pen.setWidth(2)
                line = pg.PlotDataItem(
                    x, y, name=key, symbol="o", symbolSize=5, symbolPen=symbol_pen
                )
                brush = QtGui.QBrush(QtGui.QColor(*color, 100))
                line.setFillBrush(brush)
                line.setFillLevel(0)
                self.lines[key] = line
                self.graphWidget.addItem(line)
            else:
                line = self.lines[key]
                line.setData(x, y)

        self.graphWidget.show()

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

        #     # print("out", i, temp, j)

        #     while j < 2 and i < num:

        #         # print("here", i, temp, j)

        #         info = [
        #             self.fishes[i].getFishData().getId(),
        #             self.fishes[i].getFishData().getState(),
        #             self.fishes[i].getFishData().getStatus(),
        #             self.fishes[i].getFishData().getGenesis(),
        #             str(self.fishes[i].getFishData().lifetime),
        #         ]

        #         self.grid.addWidget(FishFrame(info, self.widget), temp, j)

        #         i += 1

        #         j += 1

        #     j = 0

        #     temp += 1

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        # Add Background colour to white
        self.graphWidget.setBackground("w")
        # Add Title
        self.graphWidget.setTitle("Pond Population", color="b", size="25pt")
        # Add Axis Labels
        styles = {"color": "#f00", "font-size": "20px"}
        self.graphWidget.setLabel("left", "Population", **styles)
        self.graphWidget.setLabel("bottom", "Time", **styles)
        # Add legend
        self.graphWidget.addLegend()
        # Add grid
        self.graphWidget.showGrid(x=True, y=True)
        # Set Range
        self.vbox.addWidget(self.label)
        self.vbox.addWidget(self.graphWidget)

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

    def plot(self, x, y, plotname, color):
        pen = pg.mkPen(color=color)
        self.graphWidget.plot(
            x,
            y,
            name=plotname,
            pen=pen,
            symbolBrush=(color),
        )

    def update(fishes):

        pass
