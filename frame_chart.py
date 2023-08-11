import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tkinter as tk
from custom_data import CustomData
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config import ConfigSingleton

from fft import filter, fft

from enum import Enum

DATA_FREQUENCY = ConfigSingleton().get_config()["DATA_FREQUENCY"]
DATA_PRINT_AVG_COUNT = ConfigSingleton().get_config()["DATA_FREQUENCY"]


class ChartMode(Enum):
    TIME = 0
    FFT = 1


class FrameChart:
    def __init__(
        self,
        custome_data: CustomData,
        master: tk.Frame,
        chart_mode: ChartMode,
        lowpass_cutoff_entry: tk.Entry,
        highpass_cutoff_entry: tk.Entry,
    ):
        self.fig, self.ax = plt.subplots()
        (self.line,) = self.ax.plot([], [], lw=2, label="Time Series")
        self.ax.set_ylabel("Value")
        self.master = master
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.custom_data = custome_data

        self.ax.relim()
        self.ax.autoscale_view()

        self.schedule_id = self.master.after(1000, self.update)
        self.chart_mode = chart_mode
        self.lowpass_cutoff_entry = lowpass_cutoff_entry
        self.highpass_cutoff_entry = highpass_cutoff_entry

    def __del__(self):
        self.stop()

    def stop(self):
        self.master.after_cancel(self.schedule_id)
        plt.close()

    def update(self):
        if self.chart_mode == ChartMode.TIME:
            prcessed_data = self.custom_data.get_processed_data()
            if prcessed_data:
                print(f"Got processed data length: {len(prcessed_data)}")
                times, data = zip(*prcessed_data)
                if self.chart_mode == ChartMode.TIME:
                    filtered = filter(
                        data,
                        DATA_FREQUENCY / DATA_PRINT_AVG_COUNT,
                        self.lowpass_cutoff_entry.get(),
                        self.highpass_cutoff_entry.get(),
                    )
                    self.line.set_data(times, filtered)
                    # Format x-axis tick labels as time
                    time_format = "%H:%M:%S"
                    ticks = times[::100]
                    self.ax.set_xticks(ticks)
                    self.ax.set_xticklabels(
                        [dt.strftime(time_format) for dt in ticks],
                        rotation=45,
                        ha="right",
                    )
                    self.ax.set_xlabel("Time")
                    self.ax.set_ylabel("Magnetic field strength (nt)")
        else:
            data = self.custom_data.get_original_data()
            if data:
                times, raw_data = zip(*data)
                f, fft_data = fft(raw_data, DATA_FREQUENCY)

                self.line.set_data(f, fft_data)

                self.ax.set_xlabel("Frequency (Hz)")
                self.ax.set_ylabel("Magnitude")

        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

        self.schedule_id = self.master.after(1000, self.update)
