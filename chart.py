from PyQt5 import QtChart
from PyQt5.QtChart import  QChart, QChartView, QPieSeries, QPieSlice
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt

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

class MySimpleChart(QtChart.QChart):

    def __init__(self, datas, parent=None):
        super(MySimpleChart, self).__init__(parent)
        self._datas = datas

        self.outer = QtChart.QPieSeries()
        self.set_outer_series()
        self.addSeries(self.outer)

    def set_outer_series(self):
        slices = list()
        for data in self._datas:
            slice_ = QtChart.QPieSlice(data.name, data.value)
            slice_.setLabelVisible()
            slice_.setColor(data.primary_color)
            slice_.setLabelBrush(data.primary_color)

            slices.append(slice_)
            self.outer.append(slice_)
            
            slice_.setLabel(data.name)

        # label styling
        #for slice_ in slices:
            #percentages_str += f"{genesis}: {p * 100:.2f}%\n"
            #label = "<p align='center' style='color:{}'>{}%</p>".format(round(slice_.percentage()*100, 2))
            #label = "".format(round(slice_.percentage()*100, 2))
            #slice_.setLabel("123")

'''

class Chart(QMainWindow):
    def __init__(self):
        super().__init__()
 
        self.setWindowTitle("PyQtChart Pie Chart")
        self.setGeometry(100,100, 1280,600)
 
        self.show()
 
        self.create_piechart()
 
 
 
    def create_piechart(self):
 
        series = QPieSeries()
        series.append("Python", 80)
        series.append("C++", 70)
        series.append("Java", 50)
        series.append("C#", 40)
        series.append("PHP", 30)
 
 
 
        #adding slice
        slice = QPieSlice()
        slice = series.slices()[2]
        slice.setExploded(True)
        slice.setLabelVisible(True)
        slice.setPen(QPen(Qt.darkGreen, 2))
        slice.setBrush(Qt.green)
 
 
 
 
        chart = QChart()
        chart.legend().hide()
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTitle("Pie Chart Example")
 
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
 
        chartview = QChartView(chart)
        chartview.setRenderHint(QPainter.Antialiasing)
 
        self.setCentralWidget(chartview)
        '''