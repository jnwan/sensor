import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
from datetime import datetime


class LiveTimeSeriesPlot:
    def __init__(self, maxlen=60):
        self.maxlen = maxlen
        self.data = deque(maxlen=maxlen)
        self.time_data = deque(maxlen=maxlen)
        self.fig, self.ax = plt.subplots()
        (self.line,) = self.ax.plot([], [], lw=2, label="Time Series")
        self.ax.set_ylabel("Value")
        self.animation = FuncAnimation(self.fig, self.update, interval=1000)
        self.window_name = "Time Series Chart"

    def add_data_point(self, value):
        self.data.append(value)
        self.time_data.append(datetime.now())

    def update(self, frame):
        self.line.set_data(self.time_data, self.data)
        # Format x-axis tick labels as time
        time_format = "%H:%M:%S"
        self.ax.set_xticks(self.time_data)
        self.ax.set_xticklabels(
            [dt.strftime(time_format) for dt in self.time_data], rotation=45, ha="right"
        )
        self.ax.relim()
        self.ax.autoscale_view()

    def show(self):
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
