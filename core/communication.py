# author: zuohuaiyu
# date: 2024/9/13 14:26
import struct
import serial
import time
import utils
from utils import debug


class Com:
    def __init__(self, com_port):
        self.com_port = com_port
        if self.com_port is not None:
            try:
                self.serial = serial.Serial(self.com_port, 115200, timeout=0.1)
            except serial.SerialException as e:
                debug(e)
        else:
            self.serial = None

    def auto_search(self):
        if self.serial is None:
            try:
                self.serial = self.get_v_serial()
            except serial.SerialException as e:
                self.serial = None
                debug(e)
                return False
        return True

    def send_data(self, data):
        try:
            self.serial.write(data)
            return True
        except serial.SerialException as e:
            debug(e)
            return False

    def read_data(self):
        try:
            return self.serial.readline()
        except serial.SerialException as e:
            debug(e)
            return None

    def clear(self):
        try:
            self.serial.flushInput()
            self.serial.flushOutput()
        except serial.SerialException as e:
            debug(e)
            return None

    def get_v_serial(self):
        serial_ports = utils.get_serial_ports()
        if len(serial_ports) == 1:
            return serial.Serial(serial_ports[0], 115200, timeout=0.1)
        elif len(serial_ports) >= 2:
            for sp in serial_ports:
                try:
                    s = serial.Serial(sp, 115200, timeout=0.1)
                    if self.is_running():
                        for data in self.get_data():
                            if data.__contains__(b'\x55\xbb'):
                                return s
                    s.close()
                except serial.SerialException:
                    debug("Serial port %s is not available" % sp)
            return None

    def get_version(self):
        self.send_data(self.query_payload(1))
        data = self.read_data()
        if data:
            return data[9:-1].decode()
        return None

    def get_id(self):
        self.send_data(self.query_payload(2))
        data = self.read_data()
        if data:
            return utils.bytes_to_hex(data[9:-1])
        return None

    def stop(self):
        if self.is_running():
            self.send_data(self.query_payload(5))
            self.clear()
            count = 0
            time.sleep(0.01)
            while self.is_running():
                self.stop()
                count += 1
                if count >= 10:
                    return False
            return True
        else:
            debug("The device is not running")
            return True

    def start(self):
        payload = self.query_payload(4)
        self.send_data(payload)
        count = 0
        while not self.is_running():
            self.stop()
            self.clear()
            self.send_data(payload)
            data = self.read_data()
            if data:
                print(utils.bytes_to_hex(data))
            count += 1
            if count >= 10:
                return False
        return True

    def begin(self):
        self.start()

    def restart(self):
        self.clear()
        self.stop()
        self.send_data(self.query_payload(8))
        data = self.read_data()
        sign = b'U\xbb\x88\x00\x00\x00\x00 \x00\xa8'
        if data.__contains__(sign):
            return True
        return False

    def is_running(self):
        self.clear()
        time.sleep(0.01)
        data = self.read_data()
        if data:
            return True
        return False

    def get_data(self, interval=10):
        self.clear()
        header = b'\x55\xbb'
        line = self.serial.read(self.serial.in_waiting)
        index = line.find(header)
        line = line[index:]
        while True:
            end = line.find(header, 1)
            while end > 0:
                yield line[:end]
                line = line[end:]
                end = line.find(header, 1)
            line += self.serial.read(self.serial.in_waiting)
            time.sleep(interval / 1000)

    def get_work_mode(self):
        if self.is_running():
            self.stop()
        self.send_data(self.query_payload(16))
        data = self.read_data()
        return int.from_bytes(data[9:-1], 'big')

    def set_work_mode(self, mode):
        """
        设置工作模式
        :param mode: 工作模式，0传输X+Y+Z，5传输X+Y+Z+RMSE
        :return:是否设置成功
        """
        self.clear()
        payload = self.request_payload(15, mode, 1)
        self.send_data(payload)
        data = self.read_data()
        sign = b'\x55\xbb\x8f\x00\x00\x00\x00\x20\x00\xaf'
        if data.__contains__(sign):
            return True
        return False

    def decode_xyz(self, data, header=b'\x55\xbb\x21'):
        if data.startswith(header):
            x = struct.unpack('f', data[9:13])[0]
            y = struct.unpack('f', data[13:17])[0]
            z = struct.unpack('f', data[17:21])[0]
            return x, y, z
        return None

    def decode_alarm(self, data, header=b'\x55\xbb\x33'):
        if data.startswith(header):
            alarm_type = int.from_bytes(data[9:10], 'big')
            alarm_name = int.from_bytes(data[10:11], 'big')
            alarm_value = struct.unpack('f', data[11:15])[0]
            alarm_limit = struct.unpack('f', data[15:19])[0]
            return alarm_type, alarm_name, alarm_value, alarm_limit
        return None

    def is_alerting(self, data):
        if data.startswith(b'\x55\xbb\x33'):
            return True
        else:
            return False

    def decode_all(self, data, header=b'\x55\xbb\x21'):
        if data.startswith(header) and len(data) == 26 and utils.parity_check(data):
            x = struct.unpack('f', data[9:13])[0]
            y = struct.unpack('f', data[13:17])[0]
            z = struct.unpack('f', data[17:21])[0]
            r = struct.unpack('f', data[21:25])[0]
            return x, y, z, r
        return None

    def get_thresholds(self):
        self.clear()
        payload = self.query_payload(10)
        self.send_data(payload)
        data = self.read_data()
        x = struct.unpack('f', data[9:13])[0]
        y = struct.unpack('f', data[13:17])[0]
        z = struct.unpack('f', data[17:21])[0]
        rmse = struct.unpack('f', data[21:25])[0]
        r = struct.unpack('f', data[25:29])[0]
        return {"x": x, "y": y, "z": z, "rmse": rmse, "r": r}

    def set_thresholds(self, x, y, z, rmse, r):
        payload = b'\x55\xbb\x09\x00\x00\x00\x00\x00\x14'
        payload += struct.pack('f', x)
        payload += struct.pack('f', y)
        payload += struct.pack('f', z)
        payload += struct.pack('f', rmse)
        payload += struct.pack('f', r)
        a = payload[2]
        for i in range(3, len(payload)):
            a = a ^ payload[i]
        payload += a.to_bytes(1, 'big')
        self.send_data(payload)
        data = self.read_data()
        return data

    def get_halt_reset_seconds(self):
        """
        获取停机复位的秒数，指的是停机后，过了多长时间会复位，单位是秒
        :return: 秒数， -1表示未读取成功
        """
        payload = self.query_payload(20)  # 0x14消息指的是查询停机后复位秒数
        self.send_data(payload)
        data = self.read_data()
        if data.startswith(b'\x55\xbb\x94'):
            return int.from_bytes(data[9:10], 'big')
        return -1

    def set_halt_reset_seconds(self, seconds):
        """
        设置停机复位的秒数，指的是停机后过了多长时间会复位，单位是秒
        :param seconds: 秒数
        :return: 成功返回True，失败返回False
        """
        payload = self.request_payload(19, seconds, 1)
        self.send_data(payload)
        data = self.read_data()
        if data == b'\x55\xbb\x93\x00\x00\x00\x00\x20\x00\xb3':
            return True
        return False

    def get_switches(self):
        """
        获取开关状态，0表示关机，1表示开机
        :return: 开关状态， -1表示未读取成功
        """
        payload = self.query_payload(23)  # 0x17消息指的是各个阈值的开关状态
        self.send_data(payload)
        data = self.read_data()
        if data.startswith(b'\x55\xbb\x97'):
            return self.decode_switches(int.from_bytes(data[9:10], 'big'))
        return -1

    def decode_switches(self, data):
        rmse = (data & 16) == 16
        r = (data & 8) == 8
        x = (data & 4) == 4
        y = (data & 2) == 2
        z = (data & 1) == 1
        return {"rmse": rmse, "r": r, "x": x, "y": y, "z": z}

    def set_switches(self, rmse=True, r=True, x=True, y=True, z=True):
        """
        设置振动阈值的开关状态，0表示关闭，1表示打开
        :param rmse: 是否打开
        :param r: 是否打开
        :param x: 是否打开
        :param y: 是否打开
        :param z: 是否打开
        :return: 成功返回True，失败返回False
        """
        switch = 0
        if z:
            switch += 1
        if y:
            switch += 2
        if x:
            switch += 4
        if r:
            switch += 8
        if rmse:
            switch += 16
        payload = self.request_payload(22, switch, 1)
        self.send_data(payload)
        data = self.read_data()
        if data == b'\x55\xbb\x96\x00\x00\x00\x00\x20\x00\xb6':
            return True
        return False

    def request_payload(self, msg_type, data, data_size):
        """
        生产通信协议的载荷
        :param msg_type:消息类型，用十进制表示
        :param data: 载荷内容
        :param data_size: 载荷的字节大小，通常为1个字节
        :return: 带有奇偶校验码的字节数组
        """
        payload = b'\x55\xbb' + msg_type.to_bytes(1, 'big') + b'\x00\x00\x00\x00\x00'
        payload += data_size.to_bytes(1, 'big') + data.to_bytes(data_size, 'big')
        a = payload[2]
        for i in range(3, len(payload)):
            a = a ^ payload[i]
        payload += a.to_bytes(1, 'big')
        return payload

    def query_payload(self, msg_type):
        """
        各种查询的载荷
        :param msg_type:消息类型
        :return: 带有奇偶校验码的字节数组
        """
        payload = b'\x55\xbb' + msg_type.to_bytes(1, 'big') + b'\x00\x00\x00\x00\x00\00' + msg_type.to_bytes(1, 'big')
        return payload

    def show_some(self, length=10):
        if not self.is_running():
            self.start()
        i = 0
        for data in self.get_data():
            print(utils.bytes_to_hex(data))
            i += 1
            if i > length:
                break
