import attr
import json
from typing import List, Optional
from datetime import datetime
import os


@attr.s(auto_attribs=True)
class Mqtt:
    ip: str
    port: int
    user: str
    password: str


@attr.s(auto_attribs=True)
class Sensor:
    work_mode: int
    thresholds: dict
    halt_reset_seconds: int
    switches: dict
    shutdown_switch: int
    measure_range: int
    transmit_frequency: int
    relay_switch: int


@attr.s(auto_attribs=True)
class Config:
    mqtt: Mqtt
    sensor: Sensor
    queue_cache_size: int
    before_alarm_count: int
    float_places: int
    publish_original: bool
    # email: Optional[str] = None
    # addresses: List[Address] = attr.Factory(list)
    # created_at: datetime = attr.Factory(datetime.now)

    @classmethod
    def from_json_file(cls, filepath: str) -> 'Config':
        """从JSON文件加载Config对象"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 转换Mqtt对象
        if 'mqtt' in data:
            data['mqtt'] = Mqtt(**data['mqtt'])
        # 转换Sensor对象
        if 'sensor' in data:
            data['sensor'] = Sensor(**data['sensor'])

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


# 使用示例
# def main():
#     # 创建示例数据
#     mqtt = Mqtt(ip="127.0.0.1", port=1883, user="", password="")
#     sensor = Sensor(work_mode=0, thresholds={"x": 50, "y": 50, "z": 50, "r": 50, "rmse": 50},
#                     switches={"x": True, "y": True, "z": True, "r": False, "rmse": False}, halt_reset_seconds=5,
#                     shutdown_switch=1, measure_range=40,  transmit_frequency=100, relay_switch=0)
#
#     config = Config(
#         mqtt=mqtt,
#         sensor=sensor
#     )
#
#     # 保存到文件
#     config.to_json_file("config.json")
#     print(f"Config data saved to config.json")
#
#     # 从文件加载
#     loaded_config = Config.from_json_file("config.json")
#     print(f"Loaded config: {loaded_config}")
#
#     # 验证数据
#     assert loaded_config.mqtt.ip == config.mqtt.ip
#     assert loaded_config.mqtt.port == config.mqtt.port
#     assert loaded_config.mqtt.user == config.mqtt.user
#     assert loaded_config.mqtt.password == config.mqtt.password
#     assert loaded_config.sensor.work_mode == config.sensor.work_mode
#     assert loaded_config.sensor.thresholds == config.sensor.thresholds
#     assert loaded_config.sensor.switches == config.sensor.switches
#     assert loaded_config.sensor.halt_reset_seconds == config.sensor.halt_reset_seconds
#     assert loaded_config.sensor.baud == config.sensor.baud
#     assert loaded_config.sensor.protocol_header == config.sensor.protocol_header
#     # assert loaded_config.age == config.age
#     # assert len(loaded_config.addresses) == len(config.addresses)
#     print("Data verification passed!")
#
#
# if __name__ == "__main__":
#     main()
