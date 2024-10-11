# This is a sample Python script.
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow
from gui.mcps_mainForm import MainWindow
from gui.setting import Setting
from core.mqtt import MqttClient
from web_api.lrc_client import LrcClient


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app = QApplication(sys.argv)
    setting = Setting.from_json_file("gui/setting.json")
    mqtt_client = MqttClient()
    mqtt_client.connect(setting.mqtt.ip, setting.mqtt.port)
    mqtt_client.start_subscribe()
    lrc_client = LrcClient(setting.base_url)
    main_window = MainWindow(mqtt_client, lrc_client)
    main_window.show()
    sys.exit(app.exec_())
