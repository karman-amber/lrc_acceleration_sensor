# author: zuohuaiyu
# date: 2024/10/10 11:00

import sys
import pandas as pd
# from PyQt5 import QtGui
from PyQt5.QtWidgets import (QApplication, QWidget, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QDialog, QLabel, QGridLayout, QSizePolicy)
# from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# from web_api.lrc_client import LrcClient


class DetailDialog(QDialog):
    def __init__(self, row_data):
        super().__init__()
        self.setWindowTitle("报警时详细信息")
        self.setModal(True)
        self.resize(800, 600)

        layout = QVBoxLayout()
        # dict_keys = list(row_data.keys())
        dict_keys = {"alarm_id": "警情标识",
                     "alarm_start_time": "开始时间",
                     "alarm_end_time": "结束时间",
                     "alarm_category": "报警类别",
                     "alarm_name": "报警名称",
                     "alarm_limit": "警情阈值",
                     "alarm_min_value": "报警时最小值",
                     "alarm_max_value": "报警值最大值",
                     "alarm_interval": "持续秒数",
                     "alarm_values": "警情数据"}
        # 创建网格布局用于显示数据
        grid_layout = QGridLayout()
        for i, (key, value) in enumerate(row_data.items()):
            if i == len(row_data.items()) - 1:  # 跳过最后一列，因为它将用于绘图
                continue
            grid_layout.addWidget(QLabel(f"{dict_keys[key]}:"), i, 0)
            grid_layout.addWidget(QLabel(str(value)), i, 1)

        # 获取最后一列的数据并转换为数组
        last_column_key = list(row_data.keys())[-1]
        last_column_data = row_data[last_column_key]
        try:
            data_array = [float(x) for x in last_column_data.split(',')]

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
    def __init__(self, father=None):
        super().__init__()
        self.father = father
        self.df = None
        self.columns = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('报警数据查看')
        self.resize(600, 400)

        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.itemDoubleClicked.connect(self.showDetail)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.table)

        self.setLayout(layout)

        # 加载CSV数据
        if self.father is None or self.father.http_client is None:
            df, columns = self.load_local_alarm()
        else:
            df, columns = self.load_remote_alarm()
        self.show_alarm(df, columns)

    def load_remote_alarm(self):
        data = self.father.http_client.get_data(page=1, per_page=25)
        columns = self.father.http_client.get_columns()
        if data is None:
            return
        df = pd.DataFrame(data['data'])
        df = df.sort_values(by='alarm_start_time', ascending=False)
        return df, columns

    def load_local_alarm(self):
        # 读取本地CSV文件
        filename = 'db/lrc_alarm.csv'
        df = pd.read_csv(filename)
        df = df.sort_values(by='alarm_start_time', ascending=False)
        columns = df.columns.tolist()
        return df, columns

    def show_alarm(self, df, columns):
        self.table.setRowCount(df.shape[0])
        self.table.setColumnCount(df.shape[1] - 1)
        dict_keys = {"alarm_id": "警情标识",
                     "alarm_start_time": "开始时间",
                     "alarm_end_time": "结束时间",
                     "alarm_category": "报警类别",
                     "alarm_name": "报警名称",
                     "alarm_limit": "警情阈值",
                     "alarm_min_value": "报警时最小值",
                     "alarm_max_value": "报警值最大值",
                     "alarm_interval": "持续秒数",
                     "alarm_values": "警情数据"}
        chinese_cols = [dict_keys[col] for col in columns[:-1]]
        self.table.setHorizontalHeaderLabels(chinese_cols)
        for row in range(df.shape[0]):
            index = 0
            for col in columns:
                item = QTableWidgetItem(str(df.iloc[row][col]))
                self.table.setItem(row, index, item)
                index += 1
        self.table.resizeColumnsToContents()
        self.df = df                # 保存DataFrame以供后续使用
        self.columns = columns

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

# if __name__ == '__main__':
#     main()
