# author: zuohuaiyu
# date: 2024/10/21 16:10
import struct

import core.utils as utils

FRAME_HEADER = b'\x55\xbb'


class Protocol:
    def __init__(self):
        self.message_bytes = None
        self.header = b'\x55\xbb'
        self.message_type = b'\x00'
        self.reserved = b'\x00\x00\x00\x00'
        self.message_sub_type = 0
        self.message_length = 0
        self.message_body = bytes()
        self.check_code = 0

    def __str__(self):
        return f"{utils.bytes_to_hex(self.message_bytes)}"

    def create_request_message(self, message_type: int):
        self.message_type = message_type.to_bytes(1, 'little')
        message = b"\x55\xbb" + self.message_type + b"\x00\x00\x00\x00"
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
            result = result and self.header == FRAME_HEADER
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
            if len(message_bytes) >= 10 and FRAME_HEADER == message_bytes[:2]:
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
        if message_bytes.startswith(FRAME_HEADER):
            self.message_bytes = message_bytes
            self.decode_message()
            return True
        else:
            return False
        # print(utils.bytes_to_hex(message_bytes))

    def message_number(self):
        return self.message_type[0]

    def is_alarm(self):
        return self.message_type == b'\x33'

    def decode_alarm(self):
        data = self.message_bytes
        if self.is_alarm():
            alarm_type = int.from_bytes(data[9:10], 'little')
            alarm_name = int.from_bytes(data[10:11], 'little')
            alarm_value = struct.unpack('<f', data[11:15])[0]
            alarm_limit = struct.unpack('<f', data[15:19])[0]
            return alarm_type, alarm_name, alarm_value, alarm_limit
        return None