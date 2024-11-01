from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox
from PyQt5.QtCore import QTimer
import pyqtgraph as pg


class DynamicPlot(QWidget):
    def __init__(self, mqtt):
        super().__init__()
        self.data = {"x": [0.0], "y": [0.0], "z": [0.0]}
        self.setWindowTitle('碰撞保护实时数据图')
        self.topic = {"x": "lrc/sensor/x", "y": "lrc/sensor/y", "z": "lrc/sensor/z"}
        self.mqtt = mqtt
        self.max_value = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.plots = dict()

        # 创建下拉框
        # self.comboBox = QComboBox()
        # self.comboBox.addItems(['X轴数据', 'Y轴数据', 'Z轴数据', 'RMSE数据'])
        # self.comboBox.currentIndexChanged.connect(self.change_plot_type)

        # 创建PlotWidget实例
        self.plotWidgets = {"x": pg.PlotWidget(), "y": pg.PlotWidget(), "z": pg.PlotWidget()}
        for key, widget in self.plotWidgets.items():
            widget.setBackground('black')  # 设置背景颜色为黑色
            self.plots[key] = widget.plot(self.data[key], pen='yellow')
            widget.setLabel('left', f"{key}轴加速度")
            widget.setLabel('bottom', "时间")
            widget.setTitle(f"{key}轴实时数据曲线")
            self.data[key].clear()
            # if key not in self.mqtt.queues or self.mqtt.queues[self.topic[key]].empty():
            #     widget.setTitle(f"{key}轴实时数据曲线-已暂停")
            # else:
            #     while not self.mqtt.queues[self.topic[key]].empty():
            #         v = self.mqtt.queues[self.topic[key]].get()
            #         self.data[key].append(float(v))
            # self.plots[key].setData(self.data[key])
        # # 绘制初始曲线
        # self.plot = self.plotWidget.plot(self.data, pen='yellow')
        # # 初始化数据
        # self.change_topic("x")
        #
        # self.plotWidget_y = pg.PlotWidget()
        # self.plotWidget_y.setBackground('black')  # 设置背景颜色为黑色
        #
        # # 绘制初始曲线
        # self.plot_y = self.plotWidget_y.plot(self.data, pen='yellow')
        # # 初始化数据
        # # self.change_topic("x")

        # 创建定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(100)

        # 布局
        layout = QVBoxLayout()
        # layout.addWidget(self.comboBox)
        for key, widget in self.plotWidgets.items():
            layout.addWidget(widget)
        self.setLayout(layout)

    def update_plot(self):
        # 更新数据
        for key, widget in self.plotWidgets.items():
            topic = self.topic[key]
            if topic not in self.mqtt.queues or self.mqtt.queues[topic].empty():
                widget.setTitle(f"{key}轴实时数据曲线-已暂停")
            else:
                count = self.mqtt.queues[topic].qsize()
                if count > 1:
                    for i in range(count):
                        data = float(self.mqtt.queues[topic].get(block=False))
                        self.data[key].append(data)
                    widget.setTitle(f"{key}轴实时数据曲线")
            if len(self.data[key]) > 2000:
                self.data[key] = self.data[key][-2000:]
            # 更新曲线
            self.plots[key].setData(self.data[key])

