import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
import random
from core.mqtt import MqttClient


class DynamicPlot(QWidget):
    def __init__(self, mqtt):
        super().__init__()
        self.setWindowTitle('碰撞保护实时数据图')
        self.topic = "lrc/sensor/x"

        # 创建下拉框
        self.comboBox = QComboBox()
        self.comboBox.addItems(['X轴数据', 'Y轴数据', 'Z轴数据', 'RMSE数据'])
        self.comboBox.currentIndexChanged.connect(self.change_plot_type)

        # 创建PlotWidget实例
        self.plotWidget = pg.PlotWidget()
        self.plotWidget.setBackground('w')  # 设置背景颜色为白色

        # 初始化数据
        self.data = [0] * 100

        # 绘制初始曲线
        self.plot = self.plotWidget.plot(self.data, pen='r')

        # 设置坐标轴
        self.plotWidget.setLabel('left', "Y轴")
        self.plotWidget.setLabel('bottom', "X轴")

        # 设置标题
        self.plotWidget.setTitle("实时数据曲线")

        # 创建定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(100)

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.comboBox)
        layout.addWidget(self.plotWidget)
        self.setLayout(layout)
        self.mqtt = mqtt

    def change_plot_type(self, index):
        # 根据下拉框的索引选择不同的数据源
        if index == 0:
            self.topic = "lrc/sensor/x"
        elif index == 1:
            self.topic = "lrc/sensor/y"
        elif index == 2:
            self.topic = "lrc/sensor/z"
        elif index == 3:
            self.topic = "lrc/sensor/r"
        else:
            self.topic = "lrc/sensor/x"
        self.data.clear()
        self.data = [0] * 100
        for i in range(100):
            self.data.append(self.mqtt.queues[self.topic].get())
        self.plot.setData(self.data)

    def update_plot(self):
        # 更新数据
        self.data.append(self.mqtt.queues[self.topic].get())
        if len(self.data) > 100:
            self.data.pop(0)

        # 更新曲线
        self.plot.setData(self.data)
