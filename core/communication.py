# author: zuohuaiyu
# date: 2024/9/13 14:26
import struct
import serial
import time
import core.utils as utils
from core.utils import debug
from core.protocol import Protocol, HEADER_BYTES,HEADER_LENGTH, TYPE_LENGTH, RESERVED_LENGTH,LENGTH_FIELD_SIZE,CHECKSUM_LENGTH


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
        self.protocol = Protocol()

    def auto_search(self):
        if self.serial is not None:
            self.serial.close()
        try:
            self.serial = self.get_v_serial()
        except serial.SerialException as e:
            self.serial = None
            debug(e)
            return False
        return self.serial is not None

    def send_data(self, data):
        try:
            self.serial.write(data)
            return True
        except serial.SerialException as e:
            debug(e)
            return False

    def read_data(self, frame_length=1024):
        try:
            return self.serial.read(frame_length)
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
        data = self.__query__(1)
        if data:
            return data[9:-1].decode()
        return None

    def get_id(self):
        data = self.__query__(2)
        if data:
            return utils.bytes_to_hex(data[9:-1])
        return None

    def stop(self):
        if self.is_running():
            # self.send_data(self.query_payload(5))
            self.__query__(5)
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
        # payload = self.query_payload(4)
        # self.send_data(payload)
        self.__query__(4)
        count = 0
        while not self.is_running():
            self.stop()
            self.clear()
            self.__query__(4)
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
        data = self.__query__(8)
        if self.protocol.message_number() == 136:
            return True
        return False

    def is_running(self):
        self.clear()
        time.sleep(0.01)
        data = self.read_data()
        if data:
            return True
        return False

    def get_data(self, interval=2):
        self.clear()
        header = HEADER_BYTES
        while True:
            try:
                # 查找帧头
                while True:
                    # 读取第一个字节
                    byte = self.serial.read(1)
                    if not byte:  # 超时，继续尝试
                        continue
                    if byte[0] != HEADER_BYTES[0]:
                        continue

                    # 读取第二个字节
                    byte = self.serial.read(1)
                    if not byte or byte[0] != HEADER_BYTES[1]:
                        continue
                    break
                # 读取数据类型
                type_byte = self.serial.read(TYPE_LENGTH)
                if not type_byte:
                    continue
                data_type = type_byte[0]
                # 跳过保留字节
                reserved = self.serial.read(RESERVED_LENGTH)
                if len(reserved) != RESERVED_LENGTH:
                    continue
                # 读取长度字段
                length_bytes = self.serial.read(LENGTH_FIELD_SIZE)
                if len(length_bytes) != LENGTH_FIELD_SIZE:
                    continue

                # 解析子类型和数据长度
                sub_type = (length_bytes[0] & 0xE0) >> 5  # 提取高字节的前3位作为子类型
                data_length = length_bytes[1]  # 低字节为数据长度

                # 读取数据
                data = self.serial.read(data_length) if data_length > 0 else b''
                if len(data) != data_length:
                    continue

                # 读取校验和
                checksum_byte = self.serial.read(CHECKSUM_LENGTH)
                if not checksum_byte:
                    continue

                # 验证校验和
                frame_data = (
                        HEADER_BYTES +
                        type_byte +
                        reserved +
                        length_bytes +
                        data +
                        checksum_byte
                )
                # debug(utils.bytes_to_hex(frame_data))
                yield frame_data
            except Exception as e:
                debug(f"Unexpected error: {e}")
                continue

        # line = self.__read__()
        # index = line.find(header)
        # line = line[index:]
        # index = 1
        # while True:
        #     end = line.find(header, index)
        #     if end > 9:
        #         yield line[:end]
        #         line = line[end:]
        #         index = 1
        #     else:
        #         index += end + 1
        #     line += self.__read__()
        #     time.sleep(interval / 1000)

    def __read__(self):
        line = None
        try:
            line = self.serial.read(self.serial.in_waiting)
        except Exception as ex:
            debug(ex)
            self.auto_search()
        if line is None:
            time.sleep(1)
            return self.__read__()
        return line

    def __query__(self, msg_number):
        request_data = self.protocol.create_request_message(msg_number)
        # self.send_data(self.query_payload(msg_number))
        return self.__request__(request_data)

    def __request__(self, request_data):
        self.send_data(request_data)
        data = self.read_data()
        self.protocol.set_message(data)
        return data

    def get_work_mode(self):
        if self.is_running():
            self.stop()
        data = self.__query__(16)
        return int.from_bytes(data[9:-1], 'big')

    def get_temperature(self):
        if self.is_running():
            self.stop()
        data = self.__query__(3)
        return struct.unpack('f', data[9:-1])[0]

    def set_work_mode(self, mode):
        """
        设置工作模式
        :param mode: 工作模式，0传输X+Y+Z，5传输X+Y+Z+RMSE
        :return:是否设置成功
        """
        self.clear()
        # payload = self.request_payload(15, mode, 1)
        payload = self.protocol.message_with_integers(15, [mode], 1)
        # self.send_data(payload)
        # data = self.read_data()
        # self.protocol.set_message(data)
        self.__request__(payload)
        # sign = b'\x55\xbb\x8f\x00\x00\x00\x00\x20\x00\xaf'
        if self.protocol.message_number() == 143:
            return True
        return False

    def get_thresholds(self):
        self.clear()
        data = self.__query__(10)
        # x = struct.unpack('<f', data[9:13])[0]
        # y = struct.unpack('<f', data[13:17])[0]
        # z = struct.unpack('<f', data[17:21])[0]
        # rmse = struct.unpack('<f', data[21:25])[0]
        # r = struct.unpack('<f', data[25:29])[0]
        if self.protocol.message_number() - 128 == 10:
            [x, y, z, rmse, r] = self.protocol.to_floats()
            return {"x": x, "y": y, "z": z, "rmse": rmse, "r": r}
        return None

    def set_thresholds(self, params):
        # payload = b'\x55\xbb\x09\x00\x00\x00\x00\x00\x14'
        # payload += struct.pack('<f', x)
        # payload += struct.pack('<f', y)
        # payload += struct.pack('<f', z)
        # payload += struct.pack('<f', rmse)
        # payload += struct.pack('<f', r)
        # a = payload[2]
        # for i in range(3, len(payload)):
        #     a = a ^ payload[i]
        # payload += a.to_bytes(1, 'big')
        x, y, z, rmse, r = params
        payload = self.protocol.message_with_floats(9, [x, y, z, rmse, r])
        # self.send_data(payload)
        # data = self.read_data()
        # return data
        self.__request__(payload)
        if self.protocol.message_number() == 137:
            return True
        return False

    # def set_thresholds(self, params):
    #     return self.set_thresholds(params["x"], params["y"], params["z"], params["rmse"], params["r"])

    def get_halt_reset_seconds(self):
        """
        获取停机复位的秒数，指的是停机后，过了多长时间会复位，单位是秒
        :return: 秒数， -1表示未读取成功
        """
        data = self.__query__(20)
        # self.protocol.set_message(data)
        if self.protocol.message_number() == 148:  # 0x94号消息
            return int.from_bytes(data[9:10], 'big')
        return -1

    def set_halt_reset_seconds(self, seconds):
        """
        设置停机复位的秒数，指的是停机后过了多长时间会复位，单位是秒
        :param seconds: 秒数
        :return: 成功返回True，失败返回False
        """
        # payload = self.request_payload(19, seconds, 1)
        payload = self.protocol.message_with_integers(19, [seconds], per_int_size=1)
        # self.send_data(payload)
        # data = self.read_data()
        # self.protocol.set_message(data)
        self.__request__(payload)
        if self.protocol.message_number() == 147:
            return True
        return False

    def get_switches(self):
        """
        获取开关状态，0表示关机，1表示开机
        :return: 开关状态， -1表示未读取成功
        """
        # payload = self.query_payload(23)  # 0x17消息指的是各个阈值的开关状态
        # payload = self.protocol.create_request_message(23)
        # self.send_data(payload)
        # data = self.read_data()
        data = self.__query__(23)
        # self.protocol.set_message(data)
        if self.protocol.message_number() == 151:

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
        # payload = self.request_payload(22, switch, 1)
        payload = self.protocol.message_with_integers(22, [switch], 1)
        # self.send_data(payload)
        # data = self.read_data()
        # self.protocol.set_message(data)
        self.__request__(payload)
        if self.protocol.message_number() == 150:
            return True
        return False

    def get_shutdown_switch(self):
        data = self.__query__(18)
        if self.protocol.message_number() == 146:
            return int.from_bytes(data[9:10], 'big') == 1
        return False

    def set_shutdown_switch(self, value):
        payload = self.protocol.message_with_integers(17, [value], per_int_size=1)
        data = self.__request__(payload)
        if self.protocol.message_number() == 145:
            return True
        return False

    def get_measure_range(self):
        data = self.__query__(38)
        if self.protocol.message_number() == 166:
            return int.from_bytes(data[9:10], 'big') * 10
        return -1

    def set_measure_range(self, value):
        payload = self.protocol.message_with_integers(37, [value // 10], per_int_size=1)
        data = self.__request__(payload)
        if self.protocol.message_number() == 165:
            return True
        return False

    def get_transmit_frequency(self):
        data = self.__query__(40)
        if self.protocol.message_number() == 40 + 128:
            return int.from_bytes(data[9:11], 'little')
        return -1

    def set_transmit_frequency(self, freq):
        payload = self.protocol.message_with_integers(39, [freq], per_int_size=2)
        data = self.__request__(payload)
        if self.protocol.message_number() == 39 + 128:
            return True
        return False

    def set_relay_switch(self, value=0):
        """
        打开继电器开关
        :param value:1为NO打开，2为NC打开，3为NC和NC都打开，0为全部关闭
        :return: 是否成功
        """
        payload = self.protocol.message_with_integers(21, [value], per_int_size=1)
        data = self.__request__(payload)
        if self.protocol.message_number() == 21 + 128:
            return True
        return False

    def get_chip_frequency(self):
        freq_dict = {0: 4000, 1: 2000, 2: 1000, 3: 500, 4: 250, 5: 125, 6: 62.5, 7: 31.25, 8: 15.625, 9: 7.8125,
                     10: 3.90625}
        data = self.__query__(6)
        if self.protocol.message_number() == 6 + 128:
            sign = int.from_bytes(data[9:10], 'little')
            if sign in freq_dict:
                return freq_dict[sign]
        return -1

    def set_chip_frequency(self, freq):
        payload = self.protocol.message_with_integers(7, [freq], per_int_size=1)
        data = self.__request__(payload)
        if self.protocol.message_number() == 7 + 128:
            return True
        return False

    def get_status(self):
        result = dict()
        result["is_running"] = self.is_running()
        self.stop()
        result["id"] = self.get_id()
        result["version"] = self.get_version()
        result["thresholds"] = self.get_thresholds()
        result["transmit_frequency"] = self.get_transmit_frequency()
        result["measure_range"] = self.get_measure_range()
        result["work_mode"] = self.get_work_mode()
        # result["relay_switch"] = self.get_relay_switch()
        result["temperature"] = round(self.get_temperature(), 1)
        result["halt_reset_seconds"] = self.get_halt_reset_seconds()
        result["chip_frequency"] = self.get_chip_frequency()
        if result["is_running"]:
            self.start()
        return result

    # def set_status(self, params):
    #     is_running = self.is_running()
    #     self.stop()
    #     # result["id"] = self.get_id()
    #     # result["version"] = self.get_version()
    #     x, y, z, rmse, r = params["thresholds"]
    #     self.set_thresholds([x, y, z, rmse, r])
    #     # result["thresholds"] = self.get_thresholds()
    #     result["transmit_frequency"] = self.get_transmit_frequency()
    #     result["measure_range"] = self.get_measure_range()
    #     result["work_mode"] = self.get_work_mode()
    #     # result["relay_switch"] = self.get_relay_switch()
    #     # result["temperature"] = round(self.get_temperature(), 1)
    #     result["halt_reset_seconds"] = self.get_halt_reset_seconds()
    #     result["chip_frequency"] = self.get_chip_frequency()
    #     if result["is_running"]:
    #         self.start()
    #     return result

    def show_some(self, length=10):
        if not self.is_running():
            self.start()
        i = 0
        for data in self.get_data():
            print(utils.bytes_to_hex(data))
            i += 1
            if i > length:
                break
