import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QMenuBar, QToolBar, QStatusBar, QAction, QTextEdit, \
    QFileDialog
from PyQt5.QtWidgets import QDesktopWidget


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.setWindowTitle("碰撞保护系统")
        # self.windowTitle = "碰撞保护系统"
        ###################################################
        # 创建菜单栏
        self.statusBar().showMessage("ready")
        menubar = self.menuBar()
        # 创建文件菜单
        home_menu = menubar.addMenu('主页')
        # 创建文件菜单项
        status_overview_action = QAction('状态概览', self)
        real_time_charts_action = QAction('实时图表', self)
        recent_event_action = QAction('最近碰撞', self)

        exit_action = QAction('退出', self)
        # 添加文件菜单项到文件菜单
        home_menu.addAction(status_overview_action)
        home_menu.addAction(real_time_charts_action)
        home_menu.addAction(recent_event_action)
        home_menu.addSeparator()  # 分隔线
        # file_menu.addSeparator()
        quick_action_menu = QMenu("快速操作", self)
        start_action = QAction("启用", self)
        quick_action_menu.addAction(start_action)
        stop_action = QAction("禁用", self)
        quick_action_menu.addAction(stop_action)
        emergency_stop_action = QAction("紧急停止", self)
        quick_action_menu.addAction(emergency_stop_action)

        threshold_menu = QMenu("阈值设置", self)
        standard_threshold_menu = QMenu("标准模式", self)
        x_threshold_action = QAction("X阈值设置", self)
        standard_threshold_menu.addAction(x_threshold_action)
        y_threshold_action = QAction("Y阈值设置", self)
        standard_threshold_menu.addAction(y_threshold_action)
        z_threshold_action = QAction("Z阈值设置", self)
        standard_threshold_menu.addAction(z_threshold_action)
        rmse_threshold_action = QAction("RMSE阈值设置", self)
        standard_threshold_menu.addAction(rmse_threshold_action)
        threshold_menu.addMenu(standard_threshold_menu)

        advanced_threshold_menu = QMenu("高级模式", self)
        dynamic_threshold_action = QAction("动态阈值设置", self)
        advanced_threshold_menu.addAction(dynamic_threshold_action)
        frequency_threshold_action = QAction("频率响应设置", self)
        advanced_threshold_menu.addAction(frequency_threshold_action)
        threshold_menu.addMenu(advanced_threshold_menu)
        menubar.addMenu(threshold_menu)

        system_config_menu = QMenu("系统配置", self)
        sensor_config_menu = QMenu("传感器配置", self)
        system_config_menu.addMenu(sensor_config_menu)
        communication_config_menu = QMenu("通信配置", self)
        system_config_menu.addMenu(communication_config_menu)
        alarm_config_menu = QMenu("报警配置", self)
        system_config_menu.addMenu(alarm_config_menu)
        menubar.addMenu(system_config_menu)

        data_manager_menu = QMenu("数据管理", self)
        live_data_menu = QMenu("实时数据", self)
        data_manager_menu.addMenu(live_data_menu)
        history_data_menu = QMenu("历史数据", self)
        data_manager_menu.addMenu(history_data_menu)
        menubar.addMenu(data_manager_menu)

        diagnosis_menu = QMenu("诊断维护", self)
        system_self_test_menu = QMenu("系统自检", self)
        diagnosis_menu.addMenu(system_self_test_menu)
        performance_analysis_menu = QMenu("性能分析", self)
        diagnosis_menu.addMenu(performance_analysis_menu)
        firmware_update_menu = QMenu("固件更新", self)
        diagnosis_menu.addMenu(firmware_update_menu)
        menubar.addMenu(diagnosis_menu)

        help_support_menu = QMenu("帮助支持", self)
        user_guide_action = QAction("用户指南", self)
        help_support_menu.addAction(user_guide_action)
        troubleshooting_guide_action = QAction("故障排除指南", self)
        help_support_menu.addAction(troubleshooting_guide_action)
        technical_support_action = QAction("技术支持", self)
        help_support_menu.addAction(technical_support_action)
        menubar.addMenu(help_support_menu)

        home_menu.addMenu(quick_action_menu)
        # file_menu.addSection("快速操作")
        home_menu.addAction(exit_action)
        # 连接菜单项和工具按钮的槽函数
        # new_action.triggered.connect(self.newFile)
        # open_action.triggered.connect(self.openFile)
        # save_action.triggered.connect(self.saveFile)
        exit_action.triggered.connect(self.exitApp)
        ###################################################
        # 创建工具栏
        toolbar = self.addToolBar('Toolbar')
        # 在工具栏中添加工具按钮
        new_button = toolbar.addAction('New')  # 清空（当前）文本编辑框
        open_button = toolbar.addAction('Open')  # 打开txt文本并添加到文本编辑框
        save_button = toolbar.addAction('Save')  # 保存文本编辑框到txt文本
        # 连接菜单项和工具按钮的槽函数
        new_button.triggered.connect(self.newFile)
        open_button.triggered.connect(self.openFile)
        save_button.triggered.connect(self.saveFile)
        ###################################################
        # 创建状态栏
        statusbar = self.statusBar()
        # 在状态栏中显示消息: 'Ready' 是要显示的文本消息，30000 是消息显示的时间（以毫秒为单位），即30秒。
        statusbar.showMessage('Ready', 30000)
        ###################################################
        # 创建文本编辑框
        self.text_edit = QTextEdit(self)
        self.setCentralWidget(self.text_edit)  # 将文本编辑框设置为主窗口的中心组件

    def newFile(self):
        self.text_edit.clear()  # 清空文本编辑框

    def openFile(self):
        try:
            # 打开文件对话框，选择txt文件并读取内容，然后显示在文本编辑框中
            file_dialog = QFileDialog(self)
            file_path, _ = file_dialog.getOpenFileName()
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as file:
                    file_contents = file.read()
                    self.text_edit.setPlainText(file_contents)
        except Exception as e:
            # 处理异常，例如显示错误消息
            print(f"Error opening file: {str(e)}")

    def saveFile(self):
        try:
            # 保存文件对话框，将文本编辑框中的内容保存到txt文件中
            file_dialog = QFileDialog(self)
            file_path, _ = file_dialog.getSaveFileName()
            if file_path:
                with open(file_path, 'w') as file:
                    file_contents = self.text_edit.toPlainText()
                    file.write(file_contents)
        except Exception as e:
            # 处理异常，例如显示错误消息
            print(f"Error saving file: {str(e)}")

    def exitApp(self):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.setWindowTitle('碰撞保护系统')
    # window.showFullScreen()
    # window.setGeometry(100, 100, 800, 300)
    # window.show()
    screen_size = QDesktopWidget().availableGeometry()
    window.setGeometry(0, 0, screen_size.width(), screen_size.height())
    window.show()
    sys.exit(app.exec_())
