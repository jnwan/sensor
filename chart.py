import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import threading


class LiveTimeSeriesPlot:
    def __init__(self, stop_flag: threading.Event, maxlen=60):
        self.maxlen = maxlen
        self.data = deque(maxlen=maxlen)
        self.time_data = deque(maxlen=maxlen)
        self.fig, self.ax = plt.subplots()
        (self.line,) = self.ax.plot([], [], lw=2, label="Time Series")
        self.ax.set_ylabel("Value")
        self.animation = FuncAnimation(self.fig, self.update, interval=1000)
        self.window_name = "Time Series Chart"
        self.stop_flag = stop_flag

        self.fig.canvas.mpl_connect("close_event", self.on_close)
        self.active = False

    def on_close(self, event):
        self.stop_flag.set()
        self.active = False

    def add_data_point(self, time, value):
        if not self.stop_flag.is_set():
            self.data.append(value)
            self.time_data.append(time)

    def update(self, frame):
        if not self.stop_flag.is_set():
            self.line.set_data(self.time_data, self.data)
            # Format x-axis tick labels as time
            time_format = "%H:%M:%S"
            self.ax.set_xticks(self.time_data)
            self.ax.set_xticklabels(
                [dt.strftime(time_format) for dt in self.time_data],
                rotation=45,
                ha="right",
            )
            self.ax.relim()
            self.ax.autoscale_view()

    def show(self):
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show(block=False)
        self.active = True
