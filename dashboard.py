import random
import time
from typing import DefaultDict, Dict

from PyQt5 import QtChart
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt

import pyqtgraph as pg
from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import * 

import consts
from Fish import FishGroup
from fishFrame import FishFrame
from chart import MySimpleChart
from collections import namedtuple


class Dashboard(QMainWindow):
    def __init__(self, fishes: FishGroup):
        super().__init__()
        self.fishes: FishGroup = fishes
        self.last_updated = time.time()
        self.label = QLabel(self)
        self.label.setFont(QFont('Arial',12))
        self.slicedata = []
        self.chart_view = MySimpleChart(self.slicedata)

        self.sliceColors = ["#82d3e5", "#cfeef5", "#fd635c", "#fdc4c1",
                            "#feb543", "#ffe3b8", "#CCCCFF", "#40E0D0", "#9FE2BF", "#FFA07A"]
        self.PieData = namedtuple(
            'Data', ['name', 'value', 'primary_color', 'secondary_color'])
        percentages = self.fishes.get_percentages()
        self.create_piechart(percentages)

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
            "Pond Population : " +
            str(self.fishes.get_total()) + "\n" + percentages_str + "\n"
        )
        label_str += f"Pond Pheremone: {pheromone}\n"

        label_str += f"\nConstants:\n \tPopulation Limit: {consts.FISHES_POND_LIMIT}\n"
        label_str += f"\tDisplay Limit: {consts.FISHES_DISPLAY_LIMIT}\n"
        label_str += f"\tBirth Rate: {consts.BIRTH_RATE}x\n"

        fish_list = self.fishes.getFishes()

        self.label.setText(label_str)
        self.update_history_graph()
        self.create_piechart(percentages)
        self.createFishFrame(fish_list)

    def create_piechart(self, percentages):
        for genesis, s in percentages.items():
            randcol1 = random.choice(self.sliceColors)
            randcol2 = random.choice(self.sliceColors)
            node = self.PieData(genesis, s, QtGui.QColor(
                randcol1), QtGui.QColor(randcol2))
            self.slicedata.append(node)
        self.chart = MySimpleChart(self.slicedata)
        self.chart_view = QtChart.QChartView(self.chart)
        self.chart_view.setRenderHint(QtGui.QPainter.Antialiasing)

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
    
    def createFishFrame(self,fish_list):

        for i in reversed(range(3,self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            self.grid.removeWidget(widget)
            widget.setParent(None)


        temp = 3
        j = 0
        for i in range(len(fish_list)):
            
            info = [
                fish_list[i].getFishData().getId(),
                fish_list[i].getFishData().getState(),
                fish_list[i].getFishData().getStatus(),
                fish_list[i].getFishData().getGenesis(),
                fish_list[i].getFishData().getLifetime()
            ]
            self.grid.addWidget(FishFrame(info, self.widget), temp, j)
            # temp +=1
            j+=1
            if j>3:
                j = 0
                temp+=1


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

        font = self.label.font()

        font.setPointSize(14)

        font.setBold(True)

        self.label.setFont(font)

        # self.createFishFrame()
        
            

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

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        # Add Background colour to white
        self.graphWidget.setBackground("w")
        # Add Title
        self.graphWidget.setTitle("Pond Population", color="b", size="12pt")
        # Add Axis Labels
        styles = {"color": "#f00", "font-size": "12px"}
        self.graphWidget.setLabel("left", "Population", **styles)
        self.graphWidget.setLabel("bottom", "Time", **styles)
        # Add legend
        self.graphWidget.addLegend()
        # Add grid
        self.graphWidget.showGrid(x=True, y=True)
        # Set Range
        self.vbox.addWidget(self.label)
        self.vbox.addWidget(self.graphWidget)

        self.vbox.addWidget(self.chart_view)

        self.vbox.addLayout(self.grid)

        self.widget.setLayout(self.vbox)

        # Scroll Area Properties

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.scroll.setWidgetResizable(True)

        self.scroll.setWidget(self.widget)

        # self.scroll.setWidget(self.graphWidget)

        self.setCentralWidget(self.scroll)

        self.setGeometry(0, 290, 600, 800)

        self.setWindowTitle("Dashboard")

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