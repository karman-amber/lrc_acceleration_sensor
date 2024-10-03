import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


class DynamicLineChart(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vibration Line Chart with Matplotlib")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # container = QWidget()
        # container.setLayout(layout)
        self.setLayout(layout)

        self.ax = self.figure.add_subplot(411)
        self.line_x, = self.ax.plot([], [], 'g-', label='X data')
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.set_title("Vibration Line Chart of X")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("X Value")
        self.ax.legend()

        self.ay = self.figure.add_subplot(412)
        self.line_y, = self.ay.plot([], [], 'r-', label='Y data')
        self.ay.set_xlim(0, 100)
        self.ay.set_ylim(0, 100)
        self.ay.set_title("Vibration Line Chart of Y")
        self.ay.set_xlabel("Time (s)")
        self.ay.set_ylabel("Y Value")
        self.ay.legend()

        self.az = self.figure.add_subplot(413)
        self.line_z, = self.az.plot([], [], 'b-', label='Z data')
        self.az.set_xlim(0, 100)
        self.az.set_ylim(0, 100)
        self.az.set_title("Vibration Line Chart of Z")
        self.az.set_xlabel("Time (s)")
        self.az.set_ylabel("Z Value")
        self.az.legend()

        self.ar = self.figure.add_subplot(414)
        self.line_r, = self.ar.plot([], [], 'y-', label='RMSE data')
        self.ar.set_xlim(0, 100)
        self.ar.set_ylim(0, 100)
        self.ar.set_title("Vibration Line Chart of RMSE")
        self.ar.set_xlabel("Time (s)")
        self.ar.set_ylabel("RMSE Value")
        self.ar.legend()

        self.figure.tight_layout()

        self.xdata = []
        self.ydata = []
        self.avg_data = []

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(100)  # Update every 100 ms

    def update_plot(self):
        x = len(self.xdata) / 10  # Convert to seconds
        y = random.randint(0, 100)

        self.xdata.append(x)
        self.ydata.append(y)

        # Calculate moving average
        if len(self.ydata) >= 5:
            avg = sum(self.ydata[-5:]) / 5
        else:
            avg = sum(self.ydata) / len(self.ydata)
        self.avg_data.append(avg)

        if len(self.xdata) > 100:  # Keep only last 100 points
            self.xdata = self.xdata[-100:]
            self.ydata = self.ydata[-100:]
            self.avg_data = self.avg_data[-100:]

        self.line_x.set_data(self.xdata, self.ydata)
        self.line_y.set_data(self.xdata, self.avg_data)
        self.line_z.set_data(self.xdata, self.avg_data)
        self.line_r.set_data(self.xdata, self.avg_data)

        # if x > 10:
        #     self.ax.set_xlim(x - 10, x)
        #     self.ay.set_xlim(x - 10, x)
        #     self.az.set_xlim(x - 10, x)

        self.ax.set_ylim(0, max(max(self.ydata), max(self.avg_data)) * 1.1)
        self.ay.set_ylim(0, max(max(self.ydata), max(self.avg_data)) * 1.1)
        self.az.set_ylim(0, max(max(self.ydata), max(self.avg_data)) * 1.1)
        self.ar.set_ylim(0, max(max(self.ydata), max(self.avg_data)) * 1.1)

        self.canvas.draw()


# if __name__ == '__main__':
#     plt.style.use('dark_background')  # Optional: use a dark theme
#     app = QApplication(sys.argv)
#     window = DynamicLineChart()
#     window.show()
#     sys.exit(app.exec_())