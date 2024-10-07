import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from typing import Callable, List, Tuple, Optional, Iterator, Any
from queue import Queue
from threading import Thread
import time
import core.mqtt as mqtt


class DataSource:
    def get_data(self) -> Tuple[float, float]:
        raise NotImplementedError


class QueueDataSource(DataSource):
    def __init__(self):
        self.queue = Queue()

    def get_data(self) -> Tuple[float, float]:
        return self.queue.get()

    def put_data(self, x: float, y: float):
        self.queue.put((x, y))


class GeneratorDataSource(DataSource):
    def __init__(self, generator: Iterator[Tuple[float, float]]):
        self.generator = generator

    def get_data(self) -> Tuple[float, float]:
        return next(self.generator)


class AnimatedLine:
    def __init__(self, ax, color: str = 'blue', max_points: int = 200):
        self.line, = ax.plot([], [], color=color)
        self.xdata, self.ydata = [], []
        self.max_points = max_points

    def update(self, x: float, y: float):
        self.xdata.append(x)
        self.ydata.append(y)

        if len(self.xdata) > self.max_points:
            self.xdata = self.xdata[-self.max_points:]
            self.ydata = self.ydata[-self.max_points:]

        self.line.set_data(self.xdata, self.ydata)
        return self.line,


class Animator:
    def __init__(self,
                 data_source: DataSource,
                 figsize: Tuple[int, int] = (8, 6),
                 max_frames: int = 100):
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.data_source = data_source
        self.animated_line = AnimatedLine(self.ax)
        self.animation = None
        self._is_running = False
        self.max_frames = max_frames

    def init_func(self):
        return self.animated_line.line,

    def update(self, frame):
        if self._is_running:
            try:
                x, y = self.data_source.get_data()
                return self.animated_line.update(x, y)
            except Exception as e:
                print(f"Error updating animation: {e}")
        return self.animated_line.line,

    def setup_animation(self,
                        interval: int = 10):
        self.animation = animation.FuncAnimation(
            self.fig,
            self.update,
            init_func=self.init_func,
            interval=interval,
            blit=True,
            save_count=self.max_frames,
            cache_frame_data=False
        )

    def start(self):
        self._is_running = True

    def stop(self):
        self._is_running = False

    def show(self):
        plt.show()

    def save(self, filename: str):
        if self.animation:
            self.animation.save(filename)
        else:
            raise ValueError("No animation to save!")

    def set_xlim(self, xmin: float, xmax: float):
        self.ax.set_xlim(xmin, xmax)

    def set_ylim(self, ymin: float, ymax: float):
        self.ax.set_ylim(ymin, ymax)


def example_with_generator():
    def sine_generator():
        x = 0
        while True:
            yield x, np.sin(x)
            x += 0.1

    data_source = GeneratorDataSource(sine_generator())
    animator = Animator(data_source, max_frames=200)

    animator.set_xlim(0, 10)
    animator.set_ylim(-1, 1)

    animator.setup_animation()
    animator.start()
    return animator


def main(mqtt_client: mqtt.MqttClient = None):
    # 创建数据生成器
    def data_generator():
        x = 0
        # mqtt_client.start_subscribe("lrc/sensor/r")
        while True:
            yield x, mqtt_client.queue.get()
            x += 1

    # 设置动画
    data_source = GeneratorDataSource(data_generator())
    animator = Animator(data_source, max_frames=1000)

    # 设置坐标轴范围
    animator.set_xlim(0, 1000)
    animator.set_ylim(-1, 1)

    # 启动动画
    animator.setup_animation()
    animator.start()
    animator.show()


if __name__ == "__main__":
    main()
