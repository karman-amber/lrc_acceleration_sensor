# author: zuohuaiyu
# date: 2024/9/19 15:02
import os

from core import communication, mqtt, utils 
from threading import Thread
import time
import queue
import numpy as np
import pandas as pd


max_size = 500


def to_string(values):
    str_v = ""
    for value in values:
        str_v += str(f"{value:.0f}-")
    return str_v[:-1]


class Alarm:
    def __init__(self):
        self.end_time = None
        self.start_time = time.time()
        self.values = []
        self.category = 0
        self.name = ""
        self.limit = 0

    def __int__(self):
        self.start_time = time.time()
        self.values = []
        self.end_time = None
        self.category = 0
        self.name = ""
        self.limit = 0

    def add(self, value):
        self.values.append(value)
        self.end_time = time.time()

    def is_same(self, a_type, a_name, a_limit, interval):
        same = self.category == a_type and self.name == a_name and self.limit == a_limit
        same = same and time.time() - self.end_time <= interval
        return same

    def interval(self):
        return self.end_time - self.start_time


class Sensor:
    def __init__(self, name):
        self.name = name
        self.com = communication.Com(None)
        self.status = "unknown"
        self.is_running = False
        self.x = queue.Queue(maxsize=max_size)
        self.y = queue.Queue(maxsize=max_size)
        self.z = queue.Queue(maxsize=max_size)
        self.r = queue.Queue(maxsize=max_size)
        self.alarm = None
        self.mqtt = None

    def start(self):
        self.com.auto_search()
        self.com.start()
        self.status = "running"
        timer = time.time()
        for data in self.com.get_data():
            if not self.is_running:
                break
            if self.com.is_alerting(data):  # 处理报警数据
                self.status = "alerting"
                try:
                    line = self.com.decode_alarm(data)  # 解码报警数据
                    if line is not None:
                        alarm_type, alarm_name, alarm_value, alarm_limit = line
                        names = {0: "x", 1: "y", 2: "z", 3: "rmse"}
                        alarm_name = names[alarm_name]
                        if self.alarm is None:  # 新建报警对象
                            self.alarm = Alarm()
                            self.alarm.category = alarm_type
                            self.alarm.name = alarm_name
                            self.alarm.limit = alarm_limit
                            self.alarm.add(alarm_value)
                            self.alarm.end_time = self.alarm.start_time
                            utils.debug("Alarm created.")
                        if self.alarm.is_same(alarm_type, alarm_name, alarm_limit, 1):  # 同一报警，存储其报警时的数据
                            self.alarm.add(alarm_value)
                            self.alarm.end_time = time.time()
                except Exception as ex:
                    utils.debug([ex, utils.bytes_to_hex(data)])
            else:
                if self.alarm is not None:  # 处于报警状态中
                    timer = time.time()
                    # self.alarm.end_time = timer
                    if timer - self.alarm.end_time > 1:
                        utils.debug(f"Alarm ends: type {self.alarm.category}, name {self.alarm.name}, "
                                    f"limit {self.alarm.limit}, max value {round(np.max(self.alarm.values), 2)}, "
                                    f"last {round(self.alarm.interval(), 2)} seconds")
                        self.save_alarm()
                        self.alarm = None
                        timer = time.time()
                        self.status = "running"
                if data is not None:  # 如果是正常的加速度速度，则将其缓存为固定大小的队列中
                    try:
                        line = self.com.decode_all(data)
                        if line is not None:
                            x, y, z, r = line
                            self.push(x, y, z, r)
                    except Exception as ex:
                        utils.debug([ex, utils.bytes_to_hex(data)])
            if time.time() - timer > 2:
                timer = time.time()
                utils.debug(self.status)

    def push(self, x, y, z, r):
        if self.x.qsize() >= self.x.maxsize:
            self.x.get()
            self.y.get()
            self.z.get()
            self.r.get()
        if self.mqtt is not None:
            self.mqtt.publish(f"{x}", topic="lrc/sensor/x")
            self.mqtt.publish(f"{y}", topic="lrc/sensor/y")
            self.mqtt.publish(f"{z}", topic="lrc/sensor/z")
            self.mqtt.publish(f"{r}", topic="lrc/sensor/r")
        self.x.put(x)
        self.y.put(y)
        self.z.put(z)
        self.r.put(r)

    def save_alarm(self):
        columns = ["alarm_id", "alarm_start_time", "alarm_end_time",
                   "alarm_category", "alarm_name", "alarm_limit", "alarm_min_value",
                   "alarm_max_value", "alarm_interval", "alarm_values"]
        str_values = to_string([i * 100 for i in self.alarm.values])
        values = zip([self.alarm.start_time],
                     [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.alarm.start_time))],
                     [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.alarm.end_time))],
                     [self.alarm.category], [self.alarm.name], [self.alarm.limit],
                     [np.min(self.alarm.values)], [np.max(self.alarm.values)],
                     [self.alarm.interval()], [str_values])
        mode = "a" if os.path.exists("db/lrc_alarm.csv") else "w"
        header = True if mode == "w" else False
        df = pd.DataFrame(values, columns=columns)
        try:
            df.to_csv("db/lrc_alarm.csv", index=False, mode=mode, header=header)
        except Exception as ex:
            utils.debug(ex)
            return False
        utils.debug("保存报警信息到文件db/lrc_alarm.csv")

    def set_mqtt(self, mqtt_ip, mqtt_port=1883, mqtt_user=None, mqtt_pwd=None):
        try:
            self.mqtt = mqtt.MqttClient()
            self.mqtt.connect(mqtt_ip, mqtt_port, mqtt_user, mqtt_pwd)
        except Exception as ex:
            utils.debug(ex)
            self.mqtt = None

    def stop(self):
        self.is_running = False
        self.com.stop()
        self.status = "stopping"

    def set_cache_size(self, size):
        self.x.maxsize = size
        self.y.maxsize = size
        self.z.maxsize = size
        self.r.maxsize = size

    def run(self):
        self.is_running = True
        thread1 = Thread(target=self.start)
        thread1.daemon = True
        thread1.start()


if __name__ == '__main__':
    v = Sensor("主轴1")
    v.com.auto_search()
    v.set_mqtt("127.0.0.1", 1886)
    v.run()
    time.sleep(1000)
    v.stop()
