# author: zuohuaiyu
# date: 2024/10/10 11:00

import sys
import pandas as pd
from PyQt5 import QtGui
from PyQt5.QtWidgets import (QApplication, QWidget, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QDialog, QLabel, QGridLayout)
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from web_api.lrc_client import LrcClient


class DetailDialog(QDialog):
    def __init__(self, row_data):
        super().__init__()
        self.setWindowTitle("报警时详细信息")
        self.setModal(True)
        self.resize(800, 600)

        layout = QVBoxLayout()

        # 创建网格布局用于显示数据
        grid_layout = QGridLayout()
        for i, (key, value) in enumerate(row_data.items()):
            if i == len(row_data.items()) - 1:  # 跳过最后一列，因为它将用于绘图
                continue
            grid_layout.addWidget(QLabel(f"{key}:"), i, 0)
            grid_layout.addWidget(QLabel(str(value)), i, 1)

        # 获取最后一列的数据并转换为数组
        last_column_key = list(row_data.keys())[-1]
        last_column_data = row_data[last_column_key]
        try:
            data_array = [int(x)/100 for x in last_column_data.split('-')]

            # 创建图表
            plt.rcParams['font.family'] = 'SimHei'  # 设置字体为黑体
            plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示为方块的问题
            fig = Figure(figsize=(5, 4))
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            ax.plot(range(len(data_array)), data_array, '-o')
            ax.set_title(f'报警数据图表')
            ax.set_xlabel('时间')
            ax.set_ylabel('加速度数值')

            # 添加网格布局和图表到主布局
            layout.addLayout(grid_layout)
            layout.addWidget(canvas)

        except Exception as e:
            error_label = QLabel(f"绘制图表时出错: {str(e)}")
            layout.addWidget(error_label)

        self.setLayout(layout)


class AlarmViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('报警数据查看')
        self.resize(600, 400)

        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.itemDoubleClicked.connect(self.showDetail)
        layout.addWidget(self.table)

        self.setLayout(layout)

        # 加载CSV数据
        self.loadCSV('../db/lrc_alarm.csv')  # 替换为您的CSV文件路径

    def loadCSV(self, filename):
        try:
            # df = pd.read_csv(filename)
            client = LrcClient()
            # df = df.sort_index(ascending=False)
            data = client.get_data()
            columns = client.get_columns()
            if data is None:
                return
            df = pd.DataFrame(data['data'])
            # model = QtGui.QStandardItemModel()
            # # 将 DataFrame 的数据填充到 QStandardItemModel 中
            # for row in df.iterrows():
            #     index = 0
            #     for col_name in columns:
            #         item = QtGui.QStandardItem(str(row[1][col_name]))
            #         model.setItem(row[0], index, item)
            #         index += 1
            #
            # self.table.setModel(model)
            self.table.setRowCount(df.shape[0])
            self.table.setColumnCount(df.shape[1] - 1)
            self.table.setHorizontalHeaderLabels(columns[:-1])
            for row in range(df.shape[0]):
                index = 0
                for col in columns:
                    item = QTableWidgetItem(str(df.iloc[row][col]))
                    self.table.setItem(row, index, item)
                    index += 1

            self.table.resizeColumnsToContents()
            self.df = df  # 保存DataFrame以供后续使用
        except Exception as e:
            print(f"加载CSV文件时出错: {str(e)}")

    def showDetail(self, item):
        row = item.row()
        row_data = self.df.iloc[row].to_dict()
        dialog = DetailDialog(row_data)
        dialog.exec_()


def main():
    app = QApplication(sys.argv)
    viewer = AlarmViewer()
    viewer.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()