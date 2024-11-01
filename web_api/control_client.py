# author: zuohuaiyu
# date: 2024/10/24 13:21
import paho.mqtt.client as mqtt
import json
import time
from typing import Dict, Optional, Callable
from core.base import SensorStatus, AlarmThresholds
# from dataclasses import dataclass
#
#
# @dataclass
# class AlarmThresholds:
#     x: float
#     y: float
#     z: float
#     rmse: float
#     r: float
#
#
# @dataclass
# class SensorStatus:
#     is_running: bool
#     id: str
#     version: str
#     thresholds: AlarmThresholds
#     transmit_frequency: int
#     measure_range: int
#     work_mode: int
#     temperature: float
#     halt_reset_seconds: int
#     chip_frequency: int


class SensorManager:
    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883):
        self.client = mqtt.Client()
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.status_callback: Optional[Callable[[SensorStatus], None]] = None
        self._setup_client()

    def _setup_client(self):
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.connect(self.broker_host, self.broker_port, 60)
        self.client.loop_start()

    def _on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        # 订阅状态返回主题
        self.client.subscribe("lrc/sensor/status")

    def _on_message(self, client, userdata, msg):
        if msg.topic == "lrc/sensor/status":
            try:
                status_dict = json.loads(msg.payload.decode())
                # 转换为DeviceStatus对象
                thresholds = AlarmThresholds(**status_dict['thresholds'])
                status = SensorStatus(
                    is_running=status_dict['is_running'],
                    id=status_dict['id'],
                    version=status_dict['version'],
                    thresholds=thresholds,
                    transmit_frequency=status_dict['transmit_frequency'],
                    measure_range=status_dict['measure_range'],
                    work_mode=status_dict['work_mode'],
                    temperature=status_dict['temperature'],
                    halt_reset_seconds=status_dict['halt_reset_seconds'],
                    chip_frequency=status_dict['chip_frequency']
                )

                if self.status_callback:
                    self.status_callback(status)
            except Exception as e:
                print(f"Error parsing status message: {e}")

    def get_status(self, callback: Callable[[SensorStatus], None]) -> None:
        """
        获取设备状态
        :param callback: 状态返回的回调函数
        """
        self.status_callback = callback
        # 发布获取状态的命令
        self.client.publish("lrc/sensor/control", "get_status:")

    def close(self):
        """关闭MQTT连接"""
        self.client.loop_stop()
        self.client.disconnect()


# # 使用示例
# def main():
#     def status_handler(status: SensorStatus):
#         print("Received device status:")
#         print(f"Device ID: {status.id}")
#         print(f"Running: {status.is_running}")
#         print(f"Version: {status.version}")
#         print(f"Temperature: {status.temperature}°C")
#         print(f"Work Mode: {status.work_mode}")
#         print("Thresholds:")
#         print(f"  X: {status.thresholds.x}")
#         print(f"  Y: {status.thresholds.y}")
#         print(f"  Z: {status.thresholds.z}")
#         print(f"  RMSE: {status.thresholds.rmse}")
#         print(f"  R: {status.thresholds.r}")
#
#     # 创建设备管理器实例
#     device_manager = SensorManager()
#
#     # 获取状态
#     device_manager.get_status(status_handler)
#
#     # 等待一段时间以接收响应
#     time.sleep(5)
#
#     # 清理资源
#     device_manager.close()
#
#
# if __name__ == "__main__":
#     main()
