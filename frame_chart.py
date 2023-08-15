import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import customtkinter
from custom_data import CustomData
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config import ConfigSingleton

from fft import filter, fft

import logging

logger = logging.getLogger(__name__)

DATA_FREQUENCY = ConfigSingleton().get_config()["DATA_FREQUENCY"]
DATA_PRINT_AVG_COUNT = ConfigSingleton().get_config()["DATA_FREQUENCY"]


class TimeChart:
    def __init__(
        self,
        custome_data: CustomData,
        master: customtkinter.CTkFrame,
        lowpass_cutoff_entry: customtkinter.CTkEntry,
        highpass_cutoff_entry: customtkinter.CTkEntry,
    ):
        self.fig, self.ax = plt.subplots()
        (self.line,) = self.ax.plot([], [], lw=2, label="Time Series")
        self.ax.set_ylabel("Value")
        self.master = master
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(
            side=customtkinter.TOP, fill=customtkinter.BOTH, expand=1
        )
        self.custom_data = custome_data

        self.ax.relim()
        self.ax.autoscale_view()

        self.lowpass_cutoff_entry = lowpass_cutoff_entry
        self.highpass_cutoff_entry = highpass_cutoff_entry
        self.running = True
        self.update()

    def __del__(self):
        self.stop()
        plt.close()

    def stop(self):
        self.running = False
        self.master.after_cancel(self.schedule_id)

    def update(self):
        if self.running:
            self.schedule_id = self.master.after(1000, self.update)
        prcessed_data = self.custom_data.get_processed_data()
        if prcessed_data:
            logger.info(f"Got processed data length: {len(prcessed_data)}")
            times, data = zip(*prcessed_data)
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

        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()


class FFTChart:
    def __init__(self, custome_data: CustomData, master: customtkinter.CTkFrame):
        self.fig, self.ax = plt.subplots()
        (self.line,) = self.ax.loglog([], [])
        self.ax.set_ylabel("Value")
        self.master = master
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(
            side=customtkinter.TOP, fill=customtkinter.BOTH, expand=1
        )
        self.custom_data = custome_data

        self.ax.relim()
        self.ax.autoscale_view()

        self.running = True

        self.update()

    def __del__(self):
        self.stop()
        plt.close()

    def stop(self):
        self.running = False
        self.master.after_cancel(self.schedule_id)

    def update(self):
        if self.running:
            self.schedule_id = self.master.after(1000, self.update)
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
