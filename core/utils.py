# author: zuohuaiyu
# date: 2024/9/13 15:02
import os
import platform
import time

import serial
import psutil


def get_serial_ports():
    """获取所有串口信息

    Returns:
        list: 串口设备列表
    """
    system = platform.system()
    serial_ports = []
    count = 256
    if system == 'Windows':
        # Windows系统下使用COM口
        for i in range(count):
            port = f'COM{i + 1}'
            try:
                s = serial.Serial(port)
                s.close()
                serial_ports.append(port)
            except serial.SerialException:
                pass
    elif system == 'Linux':
        # Linux系统下使用/dev/ttyUSB*或/dev/ttyACM*
        for i in range(count):
            usb_port = f'/dev/ttyUSB{i}'
            acm_port = f'/dev/ttyACM{i}'
            if os.path.exists(usb_port):
                serial_ports.append(usb_port)
            if os.path.exists(acm_port):
                serial_ports.append(acm_port)
    elif system == 'Darwin':
        # macOS系统下使用/dev/cu.*或/dev/tty.*
        # 具体实现方式类似于Linux
        return None
    else:
        return None
    return serial_ports


def bytes_to_hex(bytes_data):
    hex_str = ''.join(['{:02x}'.format(b) for b in bytes_data])
    return hex_str


def parity_check(frame_data, header_length=2):
    b = frame_data[-1]
    a = get_parity(frame_data[header_length:-1])
    if a == b:
        return True
    return False


def get_parity(frame_data):
    a = frame_data[0]
    for i in range(1, len(frame_data)):
        a = a ^ frame_data[i]
    return a


def payload(frame_data):
    b = frame_data[-1]
    a = frame_data[2]
    for i in range(3, len(frame_data) - 1):
        a = a ^ frame_data[i]
    if a == b:
        return True
    return False


def get_cpu_info():
    # 获取CPU信息
    cpu_count = psutil.cpu_count()  # 物理CPU核心数
    cpu_percent = psutil.cpu_percent(interval=1)  # CPU使用率
    # print(f"CPU核心数：{cpu_count}, CPU使用率：{cpu_percent}%")
    return {"cpu_count": cpu_count, "cpu_percent": cpu_percent}


def get_memory_info():
    # 获取内存信息
    mem = psutil.virtual_memory()
    # print(f"总内存：{mem.total / 1024 ** 2:.2f} MB, 已用内存：{mem.used / 1024 ** 2:.2f} MB, "
    #       f"可用内存：{mem.available / 1024 ** 2:.2f} MB")
    return {"total": mem.total / 1024 ** 2, "used": mem.used / 1024 ** 2,
            "available": mem.available / 1024 ** 2}


def get_disk_info():
    # 获取磁盘信息
    disk_partitions = psutil.disk_partitions()
    disk_info = []
    for partition in disk_partitions:
        disk_usage = psutil.disk_usage(partition.mountpoint)
        # print(
        #     f"磁盘:{partition.mountpoint}, 总容量：{disk_usage.total / 1024 ** 3:.2f} GB,"
        #     f"已用磁盘：{disk_usage.used / 1024 ** 3:.2f} GB, 可用磁盘：{disk_usage.free / 1024 ** 3:.2f} GB")
        info = {"name": partition.device, "total": disk_usage.total / 1024 ** 3,
                "used": disk_usage.used / 1024 ** 3, "available": disk_usage.free / 1024 ** 3}
        disk_info.append(info)
    return disk_info


def debug(info):
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), info)
