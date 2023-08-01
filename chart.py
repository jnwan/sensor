import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
from datetime import datetime
import csv


class LiveTimeSeriesPlot:
    def __init__(self, file_name, maxlen=60):
        self.maxlen = maxlen
        self.data = deque(maxlen=maxlen)
        self.file = open(file_name, "w", newline="")
        self.csv_writer = csv.writer(self.file)
        self.data_buf = []
        self.time_data = deque(maxlen=maxlen)
        self.fig, self.ax = plt.subplots()
        (self.line,) = self.ax.plot([], [], lw=2, label="Time Series")
        self.ax.set_ylabel("Value")
        self.animation = FuncAnimation(self.fig, self.update, interval=1000)
        self.window_name = "Time Series Chart"

    def _write_data(self):
        self.csv_writer.writerows(self.data_buf)
        self.data_buf = []

    def __del__(self):
        if hasattr(self, "file") and not self.file.closed:
            self._write_data()
            self.file.close()

    def add_data_point(self, value):
        now = datetime.now()
        time_format = "%H:%M:%S"
        time_now = now.strftime(time_format)
        self.data.append(value)
        self.time_data.append(now)

        if len(self.data_buf) > 500:
            self._write_data()
        self.data_buf.append([time_now, value])

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
