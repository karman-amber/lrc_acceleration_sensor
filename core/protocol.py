# author: zuohuaiyu
# date: 2024/10/21 16:10
import struct

import core.utils as utils

HEADER_LENGTH = 2
TYPE_LENGTH = 1
RESERVED_LENGTH = 4
LENGTH_FIELD_SIZE = 2
CHECKSUM_LENGTH = 1

# HEADER_BYTES = b'\x55\xBB'
# GET_VERSION = 0x01
# GET_ID = 0x02
# GET_TEMPERATURE = 0x03
# GET_START = 0x04
# GET_STOP = 0x05
# GET_SAMPLE_FREQUENCY = 0x06
# SET_SAMPLE_FREQUENCY = 0x07
# GET_REBOOT = 0x08
# SET_THRESHOLDS = 0x09
# GET_THRESHOLDS = 0x0A
# SET_WORK_MODE = 0x0F
# GET_WORK_MODE = 0x10
# SET_ALARM_SWITCH = 0x11
# GET_ALARM_SWITCH = 0x12
# SET_HALT_RESET_SECONDS = 0x13
# GET_HALT_RESET_SECONDS = 0x14
# SET_RELAY_SWITCH = 0x15
# SET_MONITOR_MODE = 0x16
# GET_MONITOR_MODE = 0x17
# SET_ACC_RANGE = 0x25
# GET_ACC_RANGE = 0x26
# SET_REPORT_FREQUENCY = 0x27
# GET_REPORT_FREQUENCY = 0x28
#
# REPORT_SIGN = 0x21
# ALARM_SIGN = 0x33
# RESERVED_BYTES = b'\x00\x00\x00\x00'

HEADER_BYTES = b'\x66\x99'
GET_VERSION = 0x20
GET_ID = 0x21
GET_TEMPERATURE = 0x22
GET_START = 0x23
GET_STOP = 0x24
GET_SAMPLE_FREQUENCY = 0x25
SET_SAMPLE_FREQUENCY = 0x26
GET_REBOOT = 0x27
SET_THRESHOLDS = 0x28
GET_THRESHOLDS = 0x29
SET_WORK_MODE = 0x2A
GET_WORK_MODE = 0x2B
SET_ALARM_SWITCH = 0x2C
GET_ALARM_SWITCH = 0x2D
SET_HALT_RESET_SECONDS = 0x2E
GET_HALT_RESET_SECONDS = 0x2F
SET_RELAY_SWITCH = 0x30
SET_MONITOR_MODE = 0x31
GET_MONITOR_MODE = 0x32
SET_ACC_RANGE = 0x36
GET_ACC_RANGE = 0x37
SET_REPORT_FREQUENCY = 0x38
GET_REPORT_FREQUENCY = 0x39

REPORT_SIGN = 0xEE
ALARM_SIGN = 0xCC
RESERVED_BYTES = b'\x00\x00\x00\x00'


class Protocol:

    def __init__(self):
        self.message_bytes = None
        self.header = HEADER_BYTES
        self.message_type = b'\x00'
        self.reserved = RESERVED_BYTES
        self.message_sub_type = 0
        self.message_length = 0
        self.message_body = bytes()
        self.check_code = 0

    def __str__(self):
        return f"{utils.bytes_to_hex(self.message_bytes)}"

    def create_request_message(self, message_type: int):
        self.message_type = message_type.to_bytes(1, 'little')
        message = HEADER_BYTES + self.message_type + self.reserved
        message += self.pack_message_length(0, 0)
        a = utils.get_parity(message[len(self.header):])
        message += a.to_bytes(1, 'little')
        return message

    def message_with_floats(self, message_type: int, message_values: [float], sub_message_type=0):
        self.message_type = message_type.to_bytes(1, 'little')
        message = self.header + self.message_type + self.reserved
        self.message_length = 4 * len(message_values)
        self.message_sub_type = sub_message_type
        message += self.pack_message_length(self.message_sub_type, self.message_length)
        for v in message_values:
            message += struct.pack('<f', v)
        a = utils.get_parity(message[len(self.header):])
        message += a.to_bytes(1, 'little')
        return message

    def message_with_integers(self, message_type: int, message_values: [int], per_int_size=2, sub_message_type=0):
        self.message_type = message_type.to_bytes(1, 'little')
        message = self.header + self.message_type + self.reserved
        self.message_length = per_int_size * len(message_values)
        self.message_sub_type = sub_message_type
        message += self.pack_message_length(self.message_sub_type, self.message_length)
        for v in message_values:
            message += v.to_bytes(per_int_size, 'little')
        a = utils.get_parity(message[len(self.header):])
        message += a.to_bytes(1, 'little')
        return message

    def is_right(self):
        result = True
        if self.message_bytes:
            result = result and utils.parity_check(self.message_bytes, len(self.header))
            result = result and self.header == HEADER_BYTES
        else:
            result = False
        return result

    def get_payload(self):
        message = self.header + self.message_type + self.reserved
        message += self.pack_message_length(self.message_sub_type, self.message_length)
        a = message[2]
        for i in range(3, len(message)):
            a = a ^ message[i]
        message += a.to_bytes(1, 'little')
        return message

    def pack_message_length(self, num1, num2):

        # 检查输入是否合法
        if num1 > 7 or num2 > 8191:
            raise ValueError("输入整数超出范围")

        # 将两个整数左移到对应的位置
        num1 << 13  # 将num1左移5位，占据高3位
        packed_num = num1 + num2  # 合并两个整数

        # 返回字节
        return packed_num.to_bytes(2, byteorder='big')  # 使用大端字节序

    def unpack_message_length(self, msg_bytes):

        # 将字节转换为整数
        num = int.from_bytes(msg_bytes, byteorder='big')

        # 分离两个整数
        self.message_sub_type = num >> 13  # 右移5位，获取高3位
        self.message_length = num & 0x1F  # 与0x1F(二进制11111)进行按位与，获取低5位

        return self.message_sub_type, self.message_length

    def decode_message(self):
        message_bytes = self.message_bytes
        if message_bytes:
            if len(message_bytes) >= 10 and HEADER_BYTES == message_bytes[:2]:
                self.message_type = message_bytes[2:3]
                self.reserved = message_bytes[3:7]
                x, y = self.unpack_message_length(message_bytes[7:9])
                self.message_sub_type = x
                self.message_length = y
                self.message_body = message_bytes[9:-1]
                self.check_code = message_bytes[-1]
            else:
                print("通信协议无法解析", utils.bytes_to_hex(message_bytes))

    def to_integers(self):
        if self.message_body:
            data = self.message_body
            return [int.from_bytes(data[i:i + 2], byteorder='little') for i in range(0, len(data), 2)]

    def to_floats(self):
        if self.message_body:
            data = self.message_body
            try:
                return [struct.unpack('<f', data[i:i + 4])[0] for i in range(0, len(data), 4)]
            except Exception as ex:
                print(ex)
                return None

    def set_message(self, message_bytes):
        if message_bytes.startswith(HEADER_BYTES):
            self.message_bytes = message_bytes
            self.decode_message()
            return True
        else:
            return False
        # print(utils.bytes_to_hex(message_bytes))

    def message_number(self):
        return self.message_type[0]

    def is_alarm(self):
        return self.message_type[0] == ALARM_SIGN

    def decode_alarm(self):
        data = self.message_bytes
        if self.is_alarm():
            alarm_type = int.from_bytes(data[9:10], 'little')
            alarm_name = int.from_bytes(data[10:11], 'little')
            alarm_value = struct.unpack('<f', data[11:15])[0]
            alarm_limit = struct.unpack('<f', data[15:19])[0]
            return alarm_type, alarm_name, alarm_value, alarm_limit
        return None

    def to_string(self):
        return utils.bytes_to_hex(self.message_bytes)
