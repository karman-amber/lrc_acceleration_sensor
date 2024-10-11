
from PyQt5.QtWidgets import  QWidget, QVBoxLayout, QComboBox
from PyQt5.QtCore import QTimer
import pyqtgraph as pg


class DynamicPlot(QWidget):
    def __init__(self, mqtt):
        super().__init__()
        self.data = [0] * 1
        self.setWindowTitle('碰撞保护实时数据图')
        self.topic = "lrc/sensor/x"
        self.mqtt = mqtt
        self.max_data = 0
        self.min_data = 0

        # 创建下拉框
        self.comboBox = QComboBox()
        self.comboBox.addItems(['X轴数据', 'Y轴数据', 'Z轴数据', 'RMSE数据'])
        self.comboBox.currentIndexChanged.connect(self.change_plot_type)

        # 创建PlotWidget实例
        self.plotWidget = pg.PlotWidget()
        self.plotWidget.setBackground('black')  # 设置背景颜色为黑色

        # 绘制初始曲线
        self.plot = self.plotWidget.plot(self.data, pen='yellow')
        # 初始化数据
        self.change_topic("x")

        # 创建定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(100)

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.comboBox)
        layout.addWidget(self.plotWidget)
        self.setLayout(layout)

    def change_plot_type(self, index):
        # 根据下拉框的索引选择不同的数据源
        if index == 0:
            self.change_topic("x")
        elif index == 1:
            self.change_topic("y")
        elif index == 2:
            self.change_topic("z")
        elif index == 3:
            self.change_topic("r")
        else:
            self.change_topic("x")

    def change_topic(self, topic):
        self.topic = "lrc/sensor/" + topic
        self.plotWidget.setLabel('left', f"{topic}轴加速度")
        self.plotWidget.setLabel('bottom', "时间")
        self.plotWidget.setTitle(f"{topic}轴实时数据曲线")
        # self.plotWidget.plotItem.getAxis('left').setPen('yellow')
        # self.plotWidget.plotItem.getAxis('left').setLabel
        # self.plotWidget.plotItem.getAxis('bottom').setPen('yellow')
        self.data.clear()
        self.max_data = -50
        self.min_data = 50
        # self.data = [0] * 1
        if self.topic not in self.mqtt.queues or self.mqtt.queues[self.topic].empty():
            self.plotWidget.setTitle(f"{topic}轴实时数据曲线-已暂停")
        else:
            for i in range(100):
                self.data.append(self.mqtt.queues[self.topic].get())

        self.plot.setData(self.data)

    def update_plot(self):
        # 更新数据
        if self.topic not in self.mqtt.queues or self.mqtt.queues[self.topic].empty():
            self.plotWidget.setTitle(f"{self.topic[-1:]}轴实时数据曲线-已暂停")
        else:
            data = self.mqtt.queues[self.topic].get()
            if data > self.max_data:
                self.max_data = data
            if data < self.min_data:
                self.min_data = data
            self.data.append(data)
            self.plotWidget.setTitle(f"{self.topic[-1:]}轴实时数据曲线({round(self.min_data, 2)}至{round(self.max_data, 2)})")
        if len(self.data) > 100:
            self.data.pop(0)

        # 更新曲线
        self.plot.setData(self.data)
