# author: zuohuaiyu
# date: 2024/9/19 15:02
import copy
import json
import os

from core import communication, utils
from threading import Thread
import time
import queue
import numpy as np
import pandas as pd
import paho.mqtt.client as mqtt
from core.base import SensorStatus

max_size = 500


def to_string(values, float_places):
    str_v = ""
    for value in values:
        str_v += str(f"{value:.{float_places}f},")
    return str_v[:-1]


class Alarm:
    def __init__(self):
        self.start_time = get_time_stamp()
        self.values = []
        self.end_time = get_time_stamp()
        self.category = 0
        self.name = ""
        self.limit = 0

    # def __int__(self):
    #     self.start_time = get_time_stamp()
    #     self.values = []
    #     self.end_time = get_time_stamp()
    #     self.category = 0
    #     self.name = ""
    #     self.limit = 0

    def add(self, value):
        self.values.append(value)
        self.end_time = get_time_stamp()

    def is_same(self, a_type, a_name, a_limit, interval):
        same = self.category == a_type and self.name == a_name and self.limit == a_limit
        same = same and get_time_stamp() - self.end_time <= interval
        return same

    def interval(self):
        return self.end_time - self.start_time


def get_time_stamp():
    return int(time.time() * 1000)


class Sensor:
    def __init__(self, name, ):
        self.float_places = 4
        self.before_alarm_count = 20
        self.queue_cache_size = 500
        self.publish_original = True
        self.name = name
        self.com = communication.Com(None)
        self.status = "unknown"
        self.is_running = False
        self.x = queue.Queue(maxsize=max_size)
        self.y = queue.Queue(maxsize=max_size)
        self.z = queue.Queue(maxsize=max_size)
        self.r = queue.Queue(maxsize=max_size)
        self.max_acc = [0.0, 0.0, 0.0, 0.0]  # 振动量的最大值，取值x, y, z, r的绝对值
        self.error_count = 0
        self.start_time = get_time_stamp()
        self.alarm = None
        self.mqtt = None
        self.sensor_status = None

    def start(self):
        self.com.auto_search()
        self.com.start()
        if self.sensor_status:
            self.sensor_status["is_running"] = True
        self.start_time = get_time_stamp()
        self.status = "running"
        timer = get_time_stamp()
        protocol = self.com.protocol
        for data in self.com.get_data():
            if self.mqtt is not None and self.publish_original:
                self.mqtt.publish(f"lrc/sensor/original", f"{utils.bytes_to_hex(data)}")
            if not protocol.set_message(data):
                print("set message error", utils.bytes_to_hex(data))
                continue
            if not protocol.is_right():
                self.error_count += 1
                continue
            if not self.is_running:
                break
            if protocol.is_alarm():  # 处理报警数据
                self.status = "alerting"
                try:
                    line = protocol.decode_alarm()  # 解码报警数据
                    if line is not None:
                        alarm_type, alarm_name, alarm_value, alarm_limit = line
                        names = {0: "x", 1: "y", 2: "z", 3: "rmse"}
                        alarm_name = names[alarm_name]
                        if self.mqtt is not None:
                            self.mqtt.publish(f"lrc/sensor/{alarm_name[0]}", f"{alarm_value}")
                        if self.alarm is None:  # 新建报警对象
                            self.alarm = Alarm()
                            self.alarm.category = alarm_type
                            self.alarm.name = alarm_name
                            self.alarm.limit = alarm_limit
                            pre_data = []  # 记录报警前的数据，用于展示警情和预测分析
                            if alarm_name == "x":
                                pre_data = self.x.queue.copy()
                            elif alarm_name == "y":
                                pre_data = self.y.queue.copy()
                            elif alarm_name == "z":
                                pre_data = self.z.queue.copy()
                            elif alarm_name == "rmse":
                                pre_data = self.r.queue.copy()
                            #
                            for i in range(self.before_alarm_count):
                                self.alarm.add(pre_data[i])

                            self.alarm.add(alarm_value)
                            self.alarm.end_time = self.alarm.start_time
                            utils.debug("Alarm created.")
                        if self.alarm.is_same(alarm_type, alarm_name, alarm_limit, 1):  # 同一报警，存储其报警时的数据
                            self.alarm.add(alarm_value)
                            self.alarm.end_time = get_time_stamp()
                except Exception as ex:  # 此处还需要处理错误事件
                    utils.debug(["解码警情错误:", ex, utils.bytes_to_hex(data)])
                    self.alarm = None
            else:
                if self.alarm is not None:  # 处于报警状态中
                    timer = get_time_stamp()
                    if timer - self.alarm.end_time > 1000:
                        utils.debug(f"Alarm ends: type {self.alarm.category}, name {self.alarm.name}, "
                                    f"limit {self.alarm.limit}, "
                                    f"max value {round(np.max(np.abs(self.alarm.values)), self.float_places)}, "
                                    f"last {round(self.alarm.interval(), self.float_places)} seconds")
                        self.save_alarm()
                        self.alarm = None
                        timer = get_time_stamp()
                        self.status = "running"
                if protocol.message_number() == 33:  # 如果是正常的加速度速度，则将其缓存为固定大小的队列中
                    try:
                        result = protocol.to_floats()
                        if result is not None:
                            self.push(result)
                    except Exception as ex:
                        utils.debug(["数据转化错误", ex, utils.bytes_to_hex(data)])

            if get_time_stamp() - timer > 2000:
                timer = get_time_stamp()
                utils.debug(self.status)

    def push(self, result):
        if self.x.qsize() >= self.x.maxsize:
            self.x.get()
            self.y.get()
            self.z.get()
            if not self.r.empty():
                self.r.get()
        params = ["x", "y", "z", "r"]
        queues = [self.x, self.y, self.z, self.r]
        index = 0
        for value in result:
            p = params[index]
            q = queues[index]
            self.max_acc[index] = max(self.max_acc[index], round(abs(value), self.float_places))
            if self.mqtt is not None:
                self.mqtt.publish(f"lrc/sensor/{p}", f"{value}")
                if (self.start_time - get_time_stamp()) % 2000 == 0:        # 每隔两秒发布一次计算的参考值
                    ref = {"max_x": self.max_acc[0], "max_y": self.max_acc[1],
                           "max_z": self.max_acc[2], "max_r": self.max_acc[3],
                           "error_count": self.error_count}
                    self.mqtt.publish("lrc/sensor/ref", f"{json.dumps(ref)}")
            q.put(value)
            self.max_acc[index] = max(self.max_acc[index], round(abs(value), self.float_places))
            index += 1

    def save_alarm(self):
        columns = ["alarm_id", "alarm_start_time", "alarm_end_time",
                   "alarm_category", "alarm_name", "alarm_limit", "alarm_min_value",
                   "alarm_max_value", "alarm_interval", "alarm_values"]
        str_values = to_string([i for i in self.alarm.values], self.float_places)
        values = zip([self.alarm.start_time],
                     [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.alarm.start_time / 1000))],
                     [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.alarm.end_time / 1000))],
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
            self.mqtt = mqtt.Client()
            self.mqtt.connect(mqtt_ip, mqtt_port, 60)
            self.mqtt.subscribe("lrc/sensor/control")
            self.mqtt.on_message = self.on_message
            self.mqtt.loop_start()
        except Exception as ex:
            utils.debug(ex)
            self.mqtt = None

    # def set_config(self, config):
    #     self.sensor_status = config

    def get_sensor_status(self):
        self.sensor_status = self.com.get_status()

    def set_params(self, queue_cache_size, before_alarm_count, float_places, publish_original):
        """
        设置运行时参数
        :param queue_cache_size:缓存大小
        :param before_alarm_count: 警情前多少个数据用于保存
        :param float_places: 存储数据的小数点位
        :param publish_original: 是否发布原始数据
        :return:
        """
        self.queue_cache_size = queue_cache_size
        self.before_alarm_count = before_alarm_count
        self.float_places = float_places
        self.publish_original = publish_original

    def clear(self):
        self.error_count = 0
        self.max_acc = [0.0, 0.0, 0.0, 0.0]

    def on_message(self, client, userdata, msg):
        try:
            command = msg.payload.decode()
            cmd, params = command.split(":")
            result = True
            cmds = ["start", "stop", "clear", "get_status", "get_status2",
                    "set_thresholds", "set_halt_reset_seconds", "set_transmit_frequency",
                    "set_relay_switch", "set_work_mode"]
            if cmd in cmds:
                self.com.stop()
            if cmd == "clear":
                self.clear()
            elif cmd == "set_thresholds":
                params = [float(i) for i in params.split(",")]
                result = self.com.set_thresholds(params)
                if result:
                    self.sensor_status["thresholds"]["x"] = params[0]
                    self.sensor_status["thresholds"]["y"] = params[1]
                    self.sensor_status["thresholds"]["z"] = params[2]
                    self.sensor_status["thresholds"]["rmse"] = params[3]
                    self.sensor_status["thresholds"]["r"] = params[4]
            elif cmd == "set_halt_reset_seconds":
                params = int(params)
                result = self.com.set_halt_reset_seconds(params)
                if result:
                    self.sensor_status["halt_reset_seconds"] = params
            elif cmd == "set_measure_range":
                params = int(params)
                result = self.com.set_measure_range(params)
                if result:
                    self.sensor_status["measure_range"] = params
            elif cmd == "set_transmit_frequency":
                params = int(params)
                result = self.com.set_transmit_frequency(params)
                if result:
                    self.sensor_status["transmit_frequency"] = params
            elif cmd == "set_relay_switch":
                params = int(params)
                result = self.com.set_relay_switch(params)
                if result:
                    self.sensor_status["relay_switch"] = params
            elif cmd == "set_work_mode":
                params = int(params)
                result = self.com.set_work_mode(params)
                if result:
                    self.sensor_status["work_mode"] = params
            elif cmd == "get_status":
                result = copy.deepcopy(self.sensor_status)
                # result['thresholds'] = self.sensor_status.thresholds.__dict__
                self.mqtt.publish("lrc/sensor/status", json.dumps(result))
            elif cmd == "get_status2":
                result = self.com.get_status()
                self.mqtt.publish("lrc/sensor/status", json.dumps(result))
            if self.sensor_status["is_running"]:
                self.com.start()
            if cmd == "start":
                result = self.com.start()
                if result:
                    self.sensor_status["is_running"] = True
            elif cmd == "stop":
                result = self.com.stop()
                if result:
                    self.sensor_status["is_running"] = False
            utils.debug(f"Received command: {cmd}, params: {params}, result is {result}")
        except Exception as e:
            print(f"Error processing message: {e}")

    def stop(self):
        self.is_running = False
        self.com.stop()
        if self.sensor_status:
            self.sensor_status["is_running"] = False
        self.status = "stopping"

    def set_cache_size(self, size):
        self.x.maxsize = size
        self.y.maxsize = size
        self.z.maxsize = size
        self.r.maxsize = size

    # def set_sensor(self):
    #     key = "lrc/sensor/control"
    #     while True:
    #         if key in self.mqtt.queues:
    #             cmd_queue = self.mqtt.queues[key]
    #             if not cmd_queue.empty():
    #                 cmd = cmd_queue.get()
    #                 cmd, params = cmd.split(":")
    #                 if cmd == "start":
    #                     self.com.start()
    #                 elif cmd == "stop":
    #                     self.com.stop()
    #                 elif cmd == "set_thresholds":
    #                     params = [float(i) for i in params.split(",")]
    #                     self.com.set_thresholds(params)
    #                 elif cmd == "set_halt_reset_seconds":
    #                     params = int(params)
    #                     self.com.set_halt_reset_seconds(params)
    #                 elif cmd == "set_measure_range":
    #                     params = int(params)
    #                     self.com.set_measure_range(params)
    #                 elif cmd == "set_transmit_frequency":
    #                     params = float(params)
    #                     self.com.set_transmit_frequency(params)
    #                 elif cmd == "set_relay_switch":
    #                     params = int(params)
    #                     self.com.set_relay_switch(params)
    #                 elif cmd == "set_work_mode":
    #                     params = int(params)
    #                     self.com.set_work_mode(params)
    #             else:
    #                 time.sleep(0.01)
    #         else:
    #             time.sleep(0.01)

    def run(self):
        self.is_running = True
        thread1 = Thread(target=self.start)
        thread1.daemon = True
        thread1.start()

        # thread2 = Thread(target=self.set_sensor)
        # thread2.daemon = True
        # thread2.start()


if __name__ == '__main__':
    v = Sensor("主轴1")
    v.com.auto_search()
    v.set_mqtt("127.0.0.1", 1883)
    v.run()
    time.sleep(1000)
    v.stop()
