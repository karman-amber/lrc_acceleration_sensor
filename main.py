# This is a sample Python script.
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from qtpy import QtWidgets

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from lrc_main import Ui_MainWindow
from overview import DynamicLineChart


class ManagerWindow(QMainWindow):
    def __int__(self):
        super().__init__()
        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)
        # self.statusBar()
        # self.statusBar().showMessage('Ready')
        # 创建栈窗口
        # self.stackedWidget = QStackedWidget()
        # self.setCentralWidget(self.stackedWidget)
        # self.homeWidget = DynamicLineChart()
        # self.stackedWidget.addWidget(self.homeWidget)

    # 重写窗体关闭按钮事件
    def closeEvent(self, event):

        # 弹出询问窗口
        result = QtWidgets.QMessageBox.question(self, '退出', '是否保存后退出?',
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        # 判断是否点击的Yes按钮
        if result == QtWidgets.QMessageBox.Yes:
            # 保存学员信息
            event.accept()
        else:
            # 执行关闭功能
            event.ignore()

    def on_actionMachine_Overview_triggered(self, event):
        self.statusBar().showMessage('打开主界面')
        self.stackedWidget.setCurrentWidget(self.homeWidget)

    def on_actionExit_triggered(self, event):
        self.statusBar().showMessage('退出程序')
        self.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # 创建应用程序对象M.
    app = QApplication(sys.argv)
    # 创建主窗体对象
    MainWindow = ManagerWindow()
    # 创建我们自定义的窗体对象
    ui = Ui_MainWindow()
    # 设置自定义窗体为主窗体
    ui.setupUi(MainWindow)
    MainWindow.statusBar()
    MainWindow.statusBar().showMessage('Ready')

    MainWindow.stackedWidget = QStackedWidget()
    MainWindow.setCentralWidget(MainWindow.stackedWidget)
    MainWindow.homeWidget = DynamicLineChart()
    MainWindow.stackedWidget.addWidget(MainWindow.homeWidget)

    # 设置窗体大小不可更改
    # MainWindow.setFixedSize(MainWindow.width(), MainWindow.height())
    # 显示主窗体
    MainWindow.show()
    # 设置应用程序退出
    sys.exit(app.exec_())
