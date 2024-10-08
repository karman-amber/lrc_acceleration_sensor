# author: zuohuaiyu
# date: 2024/10/08 19:54
import core.communication as com


class Config(object):

    def __init__(self):
        self.mqtt_ip = "172.0.0.1"
        self.mqtt_port = "1886"
        self.mqtt_user = None
        self.mqtt_pwd = None
        self.sensor_work_mode = 5
        self.sensor_thresholds = {"x": 50, "y": 50, "z": 50, "rmse": 50, "r": 50 }
        self.sensor_halt_reset_seconds = 5
        self.sensor_switches = {"x": True, "y": True, "z": True, "rmse": True, "r": True}
        self.serial_baud = 115200
        self.protocol_header = "55 bb"
        
    def load(self, file):
        return False

    def save(self, file):
        return True

    def upload(self, sensor: com):
        return True
