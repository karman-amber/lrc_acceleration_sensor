# author: zuohuaiyu
# date: 2024/10/25 13:13

from dataclasses import dataclass


@dataclass
class AlarmThresholds:
    """报警阈值"""
    x: float
    y: float
    z: float
    rmse: float
    r: float


@dataclass
class SensorStatus:
    """传感器状态"""
    is_running: bool
    id: str
    version: str
    thresholds: AlarmThresholds
    transmit_frequency: int
    measure_range: int
    work_mode: int
    temperature: float
    halt_reset_seconds: int
    chip_frequency: int
