import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QLabel, QPushButton, QMenuBar, QMenu, QAction,
                             QToolBar, QStatusBar, QDialog, QMessageBox,
                             QMdiArea, QMdiSubWindow)
from PyQt5.QtCore import Qt
from gui.overview import DynamicPlot
from gui.alarms import AlarmViewer
from core.mqtt import MqttClient


class SubWindow(QWidget):
    def __init__(self, title="子窗口"):
        super().__init__()
        self.initUI(title)

    def initUI(self, title):
        layout = QVBoxLayout()
        label = QLabel(f'这是{title}的内容')
        layout.addWidget(label)

        self.setLayout(layout)


class CustomDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('自定义对话框')
        self.setGeometry(300, 300, 250, 150)

        layout = QVBoxLayout()
        label = QLabel('这是一个自定义对话框')
        button = QPushButton('确定')
        button.clicked.connect(self.accept)

        layout.addWidget(label)
        layout.addWidget(button)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.central_widget = None
        self.subwindow_count = 0
        self.initUI()
        self.mqtt = MqttClient()
        self.mqtt.connect("172.8.8.229", 1883)
        self.mqtt.start_subscribe()

    def initUI(self):
        # 设置主窗口
        self.setWindowTitle('机床碰撞保护系统')
        self.setGeometry(100, 100, 800, 600)

        # 创建MDI区域
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        # 创建菜单栏
        menubar = self.menuBar()
        home_menu = menubar.addMenu('主页')
        threshold_menu = menubar.addMenu('监控阈值')
        setting_menu = menubar.addMenu("系统设置")
        data_menu = menubar.addMenu("数据管理")
        diagnostic_menu = menubar.addMenu("在线诊断")
        help_menu = menubar.addMenu('帮助手册')

        # 创建菜单项
        overview_action = QAction('监控概览', self)
        overview_action.setShortcut('Ctrl+H')
        overview_action.triggered.connect(self.overview)
        home_menu.addAction(overview_action)

        recent_event_action = QAction('最近碰撞', self)
        # recent_event_action.setShortcut('Ctrl+H')
        recent_event_action.triggered.connect(self.recent_event)
        home_menu.addAction(recent_event_action)

        home_menu.addSeparator()
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        home_menu.addAction(exit_action)

        # show_dialog_action = QAction('显示对话框', self)
        # show_dialog_action.triggered.connect(self.showDialog)
        # window_menu.addAction(show_dialog_action)
        #
        # # 窗口排列方式菜单
        # cascade_action = QAction('层叠排列', self)
        # cascade_action.triggered.connect(self.mdi.cascadeSubWindows)
        # window_menu.addAction(cascade_action)
        #
        # tile_action = QAction('平铺排列', self)
        # tile_action.triggered.connect(self.mdi.tileSubWindows)
        # window_menu.addAction(tile_action)

        about_action = QAction('关于', self)
        about_action.triggered.connect(self.showAbout)
        help_menu.addAction(about_action)

        # 创建工具栏
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        toolbar.addAction(overview_action)
        toolbar.addAction(recent_event_action)

        # 创建状态栏
        self.statusBar().showMessage('就绪')

    def createSubWindow(self):
        self.subwindow_count += 1
        sub_window = QMdiSubWindow()
        sub_widget = SubWindow(f"子窗口 {self.subwindow_count}")
        sub_window.setWidget(sub_widget)
        sub_window.setWindowTitle(f"子窗口 {self.subwindow_count}")
        self.mdi.addSubWindow(sub_window)
        sub_window.show()
        self.statusBar().showMessage(f'已创建子窗口 {self.subwindow_count}')

    def closeEvent(self, event):

        # 弹出询问窗口
        result = QtWidgets.QMessageBox.question(self, '退出', '是否保存各项配置后退出?',
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        # 判断是否点击的Yes按钮
        if result == QtWidgets.QMessageBox.Yes:
            event.accept()
            self.mqtt.stop_subscribe()
        else:
            event.ignore()

    def overview(self):
        overview = DynamicPlot(self.mqtt)
        self.setCentralWidget(overview)
        overview.show()
        return True

    def recent_event(self):
        current_form = AlarmViewer()
        self.setCentralWidget(current_form)
        current_form.show()
        return True

    def showDialog(self):
        dialog = CustomDialog()
        result = dialog.exec_()
        if result == QDialog.Accepted:
            self.statusBar().showMessage('对话框已确认')

    def showAbout(self):
        QMessageBox.about(self, '关于', '碰撞保护系统1.0 版本\n 版权所有 © 2024')
        self.statusBar().showMessage('显示关于信息')


# def main():
#     app = QApplication(sys.argv)
#     main_window = MainWindow()
#     main_window.show()
#     sys.exit(app.exec_())
#
#
# if __name__ == '__main__':
#     main()
