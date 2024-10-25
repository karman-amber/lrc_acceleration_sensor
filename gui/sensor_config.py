# author: zuohuaiyu
# date: 2024/10/24 18:10
import time

from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QGridLayout, QComboBox,
                             QDoubleSpinBox, QSpinBox, QGroupBox, QVBoxLayout,
                             QPushButton, QHBoxLayout, QApplication, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from copy import deepcopy
# from web_api.control_client import DeviceManager, DeviceStatus
from core.base import SensorStatus, AlarmThresholds


class ConfigWidget(QWidget):
    # 定义信号
    config_saved = pyqtSignal(dict)  # 当配置保存时发射信号
    config_cancelled = pyqtSignal()  # 当取消时发射信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_data = deepcopy(parent.sensor_config)  # 保存初始配置
        self.father = parent
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # 只读信息组
        readonly_group = QGroupBox("传感器静态信息")
        readonly_layout = QGridLayout()

        # 添加只读字段
        readonly_fields = [
            ("运行状态:", str(self.config_data.is_running)),
            ("版本:", self.config_data.version),
            ("ID:", self.config_data.id),
            ("温度:", f"{self.config_data.temperature:.2f}℃")
        ]

        for i, (label, value) in enumerate(readonly_fields):
            readonly_layout.addWidget(QLabel(label), i, 0)
            value_label = QLabel(value)
            value_label.setStyleSheet("color: gray;")
            readonly_layout.addWidget(value_label, i, 1)

        readonly_group.setLayout(readonly_layout)
        main_layout.addWidget(readonly_group)

        # 阈值组
        thresholds_group = QGroupBox("碰撞报警阈值设置")
        thresholds_layout = QGridLayout()


        thresholds_layout.addWidget(QLabel("x:"), 0, 0)
        self.thresholds_x = QDoubleSpinBox()
        self.thresholds_x.setRange(0, 50)
        self.thresholds_x.setValue(self.config_data.thresholds.x)
        self.thresholds_x.setDecimals(1)
        thresholds_layout.addWidget(self.thresholds_x, 0, 1)

        thresholds_layout.addWidget(QLabel("y:"), 1, 0)
        self.thresholds_y = QDoubleSpinBox()
        self.thresholds_y.setRange(0, 50)
        self.thresholds_y.setValue(self.config_data.thresholds.y)
        self.thresholds_y.setDecimals(1)
        thresholds_layout.addWidget(self.thresholds_y, 1, 1)

        thresholds_layout.addWidget(QLabel("z:"), 2, 0)
        self.thresholds_z = QDoubleSpinBox()
        self.thresholds_z.setRange(0, 50)
        self.thresholds_z.setValue(self.config_data.thresholds.z)
        self.thresholds_z.setDecimals(1)
        thresholds_layout.addWidget(self.thresholds_z, 2, 1)
        # for i, (key, value) in enumerate(self.config_data.thresholds.items()):
        #     thresholds_layout.addWidget(QLabel(f"{key}:"), i, 0)
        #     spinbox = QDoubleSpinBox()
        #     spinbox.setRange(0, 1000)
        #     spinbox.setValue(value)
        #     spinbox.setDecimals(1)
        #     self.threshold_inputs[key] = spinbox
        #     thresholds_layout.addWidget(spinbox, i, 1)

        thresholds_group.setLayout(thresholds_layout)
        main_layout.addWidget(thresholds_group)

        # 其他参数组
        params_group = QGroupBox("传感器参数设置")
        params_layout = QGridLayout()

        # 传输频率下拉框
        params_layout.addWidget(QLabel("传输频率:"), 0, 0)
        self.transmit_freq_combo = QComboBox()
        self.transmit_freq_combo.addItems(['100', '50', '200', '150'])
        self.transmit_freq_combo.setCurrentText(str(self.config_data.transmit_frequency))
        params_layout.addWidget(self.transmit_freq_combo, 0, 1)

        # 工作模式下拉框
        params_layout.addWidget(QLabel("工作模式:"), 1, 0)
        self.work_mode_combo = QComboBox()
        self.work_mode_combo.addItems(['0', '1', '2', '3', '4', '5'])
        self.work_mode_combo.setCurrentText(str(self.config_data.work_mode))
        params_layout.addWidget(self.work_mode_combo, 1, 1)

        # 芯片频率下拉框
        params_layout.addWidget(QLabel("芯片频率:"), 2, 0)
        self.chip_freq_combo = QComboBox()
        self.chip_freq_combo.addItems(['4000', '2000', '1000', '500'])
        self.chip_freq_combo.setCurrentText(str(self.config_data.chip_frequency))
        params_layout.addWidget(self.chip_freq_combo, 2, 1)

        # 测量范围
        params_layout.addWidget(QLabel("测量范围:"), 3, 0)
        self.measure_range_combo = QComboBox()
        self.measure_range_combo.addItems(['40', '20', '10'])
        self.measure_range_combo.setCurrentText(str(self.config_data.measure_range))
        params_layout.addWidget(self.measure_range_combo, 3, 1)
        # self.measure_range_spin = QSpinBox()
        # self.measure_range_spin.setRange(1, 100)
        # self.measure_range_spin.setValue(self.config_data["measure_range"])
        # params_layout.addWidget(self.measure_range_spin, 3, 1)

        # 停机重置秒数
        params_layout.addWidget(QLabel("停机重置秒数:"), 4, 0)
        self.halt_reset_spin = QSpinBox()
        self.halt_reset_spin.setRange(1, 60)
        self.halt_reset_spin.setValue(self.config_data.halt_reset_seconds)
        params_layout.addWidget(self.halt_reset_spin, 4, 1)

        params_group.setLayout(params_layout)
        main_layout.addWidget(params_group)

        # 添加按钮组
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # 添加弹性空间，使按钮靠右对齐

        # 保存按钮
        self.save_button = QPushButton("保存")
        self.save_button.setFixedWidth(80)
        self.save_button.clicked.connect(self.save_config)
        button_layout.addWidget(self.save_button)

        # 取消按钮
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setFixedWidth(80)
        self.cancel_button.clicked.connect(self.cancel_changes)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def get_config(self):
        status = self.config_data
        status.thresholds.x = self.thresholds_x.value()
        status.thresholds.y = self.thresholds_y.value()
        status.thresholds.z = self.thresholds_z.value()
        status.halt_reset_seconds = self.halt_reset_spin.value()
        status.transmit_frequency = int(self.transmit_freq_combo.currentText())
        status.measure_range = int(self.measure_range_combo.currentText())
        status.work_mode = int(self.work_mode_combo.currentText())
        status.chip_frequency = int(self.chip_freq_combo.currentText())
        return status
        # return {
        #     "is_running": self.config_data["is_running"],
        #     "id": self.config_data["id"],
        #     "version": self.config_data["version"],
        #     "thresholds": {
        #         "x": self.thresholds_x,
        #         "y": self.thresholds_y,
        #         "z": self.thresholds_z
        #     },
        #     "transmit_frequency": int(self.transmit_freq_combo.currentText()),
        #     "measure_range": self.measure_range_spin.value(),
        #     "work_mode": int(self.work_mode_combo.currentText()),
        #     "temperature": self.config_data["temperature"],
        #     "halt_reset_seconds": self.halt_reset_spin.value(),
        #     "chip_frequency": int(self.chip_freq_combo.currentText())
        # }

    def save_config(self):
        """保存配置"""
        self.father.set_sensor(self.get_config())
        QMessageBox.information(self, "提示", "配置已保存")

    def cancel_changes(self):
        """取消更改"""
        # 恢复所有控件到初始值
        self.thresholds_x.setValue(self.config_data.thresholds.x)
        self.thresholds_y.setValue(self.config_data.thresholds.y)
        self.thresholds_z.setValue(self.config_data.thresholds.z)
        self.transmit_freq_combo.setCurrentText(str(self.config_data.transmit_frequency))
        self.measure_range_combo.setCurrentText(str(self.config_data.measure_range))
        self.work_mode_combo.setCurrentText(str(self.config_data.work_mode))
        self.halt_reset_spin.setValue(self.config_data.halt_reset_seconds)
        self.chip_freq_combo.setCurrentText(str(self.config_data.chip_frequency))
        self.config_cancelled.emit()
        QMessageBox.information(self, "提示", "已取消更改")


# 使用示例
if __name__ == '__main__':
    import sys

    # 示例配置数据
    config_data = {
        "is_running": True,
        "id": "7024411f0000",
        "version": "3.0.0",
        "thresholds": {
            "x": 1.0,
            "y": 50.0,
            "z": 50.0,
            "rmse": 50.0,
            "r": 50.0
        },
        "transmit_frequency": 50,
        "measure_range": 20,
        "work_mode": 5,
        "temperature": 27.651933670043945,
        "halt_reset_seconds": 3,
        "chip_frequency": 4000
    }

    app = QApplication(sys.argv)
    widget = ConfigWidget(config_data)


    # 示例：连接信号
    def on_config_saved(new_config):
        print("配置已保存:", new_config)


    def on_config_cancelled():
        print("配置已取消")


    widget.config_saved.connect(on_config_saved)
    widget.config_cancelled.connect(on_config_cancelled)

    widget.show()
    sys.exit(app.exec_())
