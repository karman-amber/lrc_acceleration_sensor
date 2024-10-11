import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
import random
from core.mqtt import MqttClient


class DynamicPlot(QWidget):
    def __init__(self, mqtt):
        super().__init__()
        self.setWindowTitle('碰撞保护实时数据图')

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
        layout.addWidget(self.plotWidget)
        self.setLayout(layout)
        self.mqtt = mqtt

    def update_plot(self):
        # 更新数据
        self.data.append(self.mqtt.queues["lrc/sensor/x"].get())
        if len(self.data) > 100:
            self.data.pop(0)

        # 更新曲线
        self.plot.setData(self.data)
