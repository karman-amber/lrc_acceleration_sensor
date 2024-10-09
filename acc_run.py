# author: zuohuaiyu
# date: 2024/10/9 10:47
import sys

from core.sensor import Sensor
from config import Config
import time
from core.utils import debug


if __name__ == '__main__':
    v = Sensor("主轴1")
    while not v.com.auto_search():
        debug("找不到传感器设备，请先将传感器数据线插入串口.")
        time.sleep(5)
    config = Config.from_json_file("config.json")
    v.set_mqtt(config.mqtt.ip, config.mqtt.port)
    if v.mqtt is None:
        debug("mqtt连接失败！")
    v.run()
    while True:
        user_input = input("请输入指令 (输入 'stop' 退出): ")
        if user_input.lower() == 'stop':
            break
    v.stop()
