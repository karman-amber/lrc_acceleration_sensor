# author: zuohuaiyu
# date: 2024/10/9 10:47
import sys

from core.sensor import Sensor
from config import Config
import time
from core.utils import debug
from core.base import SensorStatus, AlarmThresholds

if __name__ == '__main__':
    v = Sensor("主轴1")
    while not v.com.auto_search():
        debug("找不到传感器设备，请先将传感器数据线插入串口.")
        time.sleep(5)
    config_file_path = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    config = Config.from_json_file(config_file_path)
    debug("传感器配置加载成功.")
    v.com.set_switches(rmse=config.sensor.switches["rmse"], x=config.sensor.switches["x"],
                       y=config.sensor.switches["y"], z=config.sensor.switches["z"], r=config.sensor.switches["r"])
    v.com.set_thresholds([config.sensor.thresholds["x"], config.sensor.thresholds["y"],
                          config.sensor.thresholds["z"], config.sensor.thresholds["r"],
                          config.sensor.thresholds["rmse"]])
    v.com.set_work_mode(config.sensor.work_mode)
    v.com.set_halt_reset_seconds(config.sensor.halt_reset_seconds)
    v.com.set_relay_switch(config.sensor.relay_switch)
    v.com.set_measure_range(config.sensor.measure_range)
    v.com.set_transmit_frequency(config.sensor.transmit_frequency)
    # v.com.set_shutdown_switch(config.sensor.shutdown_switch)
    debug("传感器配置应用成功.")
    v.set_mqtt(config.mqtt.ip, config.mqtt.port)
    debug(f"mqtt连接到 {config.mqtt.ip}:{config.mqtt.port}")
    if v.mqtt is None:
        debug("mqtt连接失败！")
    try:
        # status_dict = v.com.get_status()
        # # 转换为DeviceStatus对象
        # thresholds = AlarmThresholds(**status_dict['thresholds'])
        # status = SensorStatus(
        #     is_running=status_dict['is_running'],
        #     id=status_dict['id'],
        #     version=status_dict['version'],
        #     thresholds=thresholds,
        #     transmit_frequency=status_dict['transmit_frequency'],
        #     measure_range=status_dict['measure_range'],
        #     work_mode=status_dict['work_mode'],
        #     temperature=status_dict['temperature'],
        #     halt_reset_seconds=status_dict['halt_reset_seconds'],
        #     chip_frequency=status_dict['chip_frequency']
        # )
        # v.set_config(status)
        v.get_sensor_status()
    except Exception as e:
        print(f"Error parsing status message: {e}")
    v.run()
    while True:
        user_input = input("请输入指令 (输入 'stop' 退出): \n")
        if user_input.lower() == 'stop':
            v.stop()
            config.sensor.switches = v.com.get_switches()
            config.sensor.thresholds = v.com.get_thresholds()
            config.sensor.work_mode = v.com.get_work_mode()
            config.sensor.halt_reset_seconds = v.com.get_halt_reset_seconds()
            config.sensor.measure_range = v.com.get_measure_range()
            config.sensor.transmit_frequency = v.com.get_transmit_frequency()
            s = config.sensor
            if s.work_mode != -1 and s.halt_reset_seconds != -1 and s.measure_range != -1 and s.transmit_frequency != -1:
                config.to_json_file(config_file_path)
                debug("传感器配置保存本地成功.")
            else:
                debug("传感器配置获取错误，保存本地失败.")
            v.mqtt.loop_stop()
            v.mqtt.disconnect()
            break
    debug("碰撞保护监控系统已经退出.")
