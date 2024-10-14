import sys

import attr
from datetime import datetime
import os
import json

from PyQt5.QtCore import QProcess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QMessageBox


class SettingEditorWidget(QWidget):
    def __init__(self, father):
        super().__init__()
        self.father = father
        self.json_file_path = os.path.join(os.getcwd(), 'gui/setting.json')
        self.initUI()
        self.load_json()

    def initUI(self):
        layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        button_layout = QHBoxLayout()

        save_button = QPushButton('保存')
        save_button.clicked.connect(self.save_json)
        button_layout.addWidget(save_button)

        cancel_button = QPushButton('取消')
        cancel_button.clicked.connect(self.load_json)
        button_layout.addWidget(cancel_button)

        restart_button = QPushButton('重启并应用')
        restart_button.clicked.connect(self.restart_and_apply)
        button_layout.addWidget(restart_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setWindowTitle('配置编辑器')
        self.setGeometry(300, 300, 400, 300)

    def load_json(self):
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
            self.text_edit.setText(json.dumps(json_data, indent=4, ensure_ascii=False))
        except FileNotFoundError:
            QMessageBox.warning(self, '错误', f'找不到文件: {self.json_file_path}')
        except json.JSONDecodeError:
            QMessageBox.warning(self, '错误', '无效的JSON文件')

    def save_json(self):
        try:
            json_data = json.loads(self.text_edit.toPlainText())
            with open(self.json_file_path, 'w', encoding='utf-8') as file:
                json.dump(json_data, file, indent=4, ensure_ascii=False)
            QMessageBox.information(self, '成功', '配置文件已保存')
        except json.JSONDecodeError:
            QMessageBox.warning(self, '错误', '无效的JSON格式')

    def restart_and_apply(self):
        reply = QMessageBox.question(self, '确认', '确定要保存更改并重启系统吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.save_json()
            QMessageBox.information(self, "重启", "应用程序将要重启。")
            QApplication.quit()
            status = QProcess.startDetached(sys.executable, sys.argv)
            if not status:
                QMessageBox.warning(self, "错误", "无法重启应用程序。")


@attr.s(auto_attribs=True)
class Mqtt:
    ip: str
    port: int
    user: str
    password: str


# @attr.s(auto_attribs=True)
# class HttpClient:
#     ip: str
#     port: int


@attr.s(auto_attribs=True)
class Sensor:
    work_mode: int
    thresholds: dict
    halt_reset_seconds: int
    switches: dict
    baud: int
    protocol_header: str


@attr.s(auto_attribs=True)
class Setting:
    mqtt: Mqtt
    base_url: str

    # sensor: Sensor

    # email: Optional[str] = None
    # addresses: List[Address] = attr.Factory(list)
    # created_at: datetime = attr.Factory(datetime.now)

    @classmethod
    def from_json_file(cls, filepath: str) -> 'Setting':
        """从JSON文件加载Config对象"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 转换Mqtt对象
        if 'mqtt' in data:
            data['mqtt'] = Mqtt(**data['mqtt'])
        # # 转换Sensor对象
        # if 'sensor' in data:
        #     data['sensor'] = Sensor(**data['sensor'])

        # # 转换日期字符串为datetime对象
        # if 'created_at' in data:
        #     data['created_at'] = datetime.fromisoformat(data['created_at'])

        return cls(**data)

    def to_json_file(self, filepath: str) -> None:
        """将Config对象保存为JSON文件"""
        data = attr.asdict(
            self,
            filter=lambda attr, value: value is not None,
            value_serializer=self._serialize_value
        )

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _serialize_value(instance, field, value):
        """自定义序列化方法"""
        if isinstance(value, datetime):
            return value.isoformat()
        return value

# # 使用示例
# def main():
#     # 创建示例数据
#     mqtt = Mqtt(ip="127.0.0.1", port=1883, user="", password="")
#     # sensor = Sensor(work_mode=5, thresholds={"x": 50, "y": 50, "z": 50, "r": 50, "rmse": 2},
#     #                 switches={"x": True, "y": True, "z": True, "r": True, "rmse": True}, halt_reset_seconds=5,
#     #                 baud=115200, protocol_header="55 bb")
#     # http = HttpClient(ip="127.0.0.1", port=5000)
#
#     setting = Setting(
#         mqtt=mqtt,
#         base_url="http://127.0.0.1:5000"
#         # sensor=sensor
#     )
#
#     # 保存到文件
#     setting.to_json_file("setting.json")
#     print(f"Setting data saved to setting.json")
#
#     # 从文件加载
#     loaded_config = Setting.from_json_file("setting.json")
#     print(f"Loaded config: {loaded_config}")
#
#     # 验证数据
#     assert loaded_config.mqtt.ip == setting.mqtt.ip
#     assert loaded_config.mqtt.port == setting.mqtt.port
#     assert loaded_config.mqtt.user == setting.mqtt.user
#     assert loaded_config.mqtt.password == setting.mqtt.password
#     # assert loaded_config.sensor.work_mode == config.sensor.work_mode
#     # assert loaded_config.sensor.thresholds == config.sensor.thresholds
#     # assert loaded_config.sensor.switches == config.sensor.switches
#     # assert loaded_config.sensor.halt_reset_seconds == config.sensor.halt_reset_seconds
#     # assert loaded_config.sensor.baud == config.sensor.baud
#     # assert loaded_config.sensor.protocol_header == config.sensor.protocol_header
#     # assert loaded_config.age == config.age
#     # assert len(loaded_config.addresses) == len(config.addresses)
#     print("Data verification passed!")
#
#
# if __name__ == "__main__":
#     main()
