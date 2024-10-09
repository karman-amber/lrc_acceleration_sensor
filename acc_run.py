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
    debug("传感器配置加载成功.")
    v.com.set_switches(rmse=config.sensor.switches["rmse"], x=config.sensor.switches["x"],
                       y=config.sensor.switches["y"], z=config.sensor.switches["z"], r=config.sensor.switches["r"])
    v.com.set_thresholds(x=config.sensor.thresholds["x"], y=config.sensor.thresholds["y"],
                         z=config.sensor.thresholds["z"], r=config.sensor.thresholds["r"],
                         rmse=config.sensor.thresholds["rmse"])
    v.com.set_work_mode(config.sensor.work_mode)
    v.com.set_halt_reset_seconds(config.sensor.halt_reset_seconds)
    debug("传感器配置应用成功.")
    v.set_mqtt(config.mqtt.ip, config.mqtt.port)
    debug(f"mqtt连接到 {config.mqtt.ip}:{config.mqtt.port}")
    if v.mqtt is None:
        debug("mqtt连接失败！")
    v.run()
    while True:
        user_input = input("请输入指令 (输入 'stop' 退出): \n")
        if user_input.lower() == 'stop':
            break
    v.stop()
