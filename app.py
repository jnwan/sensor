import tkinter as tk
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from connect import scan_ports_and_connect
from indicator import Indicator
from data_api import write_modbus
from config import ConfigSingleton
from custom_data import CustomData, DataMode
from frame_chart import FrameChart, ChartMode
from scheduler import Scheduler

CONFIG = None
CLIENT = None


def plot_figure():
    x = np.linspace(0, 2 * np.pi, 100)
    y = np.sin(x)

    fig = Figure(figsize=(3, 2))
    ax = fig.add_subplot(111)
    ax.plot(x, y)
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.set_title("Sine Wave")
    ax.relim()
    ax.autoscale_view()

    return fig


def close(
    indicator: Indicator,
    custom_data: CustomData,
    time_chart: FrameChart,
    fft_chart: FrameChart,
    scheduler: Scheduler,
):
    time_chart.stop()
    fft_chart.stop()
    indicator.stop()
    custom_data.stop()
    scheduler.stop()


START_DEVICE_WRITE_ADDRESS = ConfigSingleton().get_config()[
    "START_DEVICE_WRITE_ADDRESS"
]
START_DEVICE_WRITE_VALUE = ConfigSingleton().get_config()["START_DEVICE_WRITE_VALUE"]
INCREASE_TEMP_WRITE_ADDRESS = ConfigSingleton().get_config()[
    "INCREASE_TEMP_WRITE_ADDRESS"
]
INCREASE_TEMP_WRITE_VALUE = ConfigSingleton().get_config()["INCREASE_TEMP_WRITE_VALUE"]
LOCK_LASER_WRITE_ADDRESS = ConfigSingleton().get_config()["LOCK_LASER_WRITE_ADDRESS"]
LOCK_LASER_WRITE_VALUE = ConfigSingleton().get_config()["LOCK_LASER_WRITE_VALUE"]

DDS_WRITE_ADDRESS = ConfigSingleton().get_config()["DDS_WRITE_ADDRESS"]
DDS_WRITE_VALUE = ConfigSingleton().get_config()["DDS_WRITE_VALUE"]


def start_device():
    global CLIENT
    write_modbus(CLIENT, START_DEVICE_WRITE_ADDRESS, START_DEVICE_WRITE_VALUE)


def increase_temp():
    global CLIENT
    write_modbus(CLIENT, INCREASE_TEMP_WRITE_ADDRESS, INCREASE_TEMP_WRITE_VALUE)


def lock_laser():
    global CLIENT
    write_modbus(CLIENT, LOCK_LASER_WRITE_ADDRESS, LOCK_LASER_WRITE_VALUE)


def start_dds():
    global CLIENT
    write_modbus(CLIENT, DDS_WRITE_ADDRESS, DDS_WRITE_VALUE)


def read_sin(custom_data: CustomData):
    custom_data.set_mode(DataMode.SIN)


def read_dds(custom_data: CustomData):
    custom_data.set_mode(DataMode.DDS)


def main():
    global CLIENT
    clients = scan_ports_and_connect()
    assert len(clients) == 1, "Can't find proper port to connect"
    CLIENT = clients[0]

    try:
        root = tk.Tk()
        root.geometry("1920x1080")  # Set the size of the window

        scheduler = Scheduler()

        # Create two frames for the sections
        left_frame = tk.Frame(root, padx=10, pady=10)  # First section with 1/3 width
        right_frame = tk.Frame(root, padx=10, pady=10)  # Second section with 2/3 width

        # Define the grid layout
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=3)

        # Place the frames on the grid
        left_frame.grid(row=0, column=0, sticky="nsew")
        right_frame.grid(row=0, column=1, sticky="nsew")

        lights_frame = tk.Frame(left_frame)
        buttons_frame = tk.Frame(left_frame)

        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=2)

        lights_frame.grid(row=0, column=0, sticky="nsew")
        buttons_frame.grid(row=1, column=0, sticky="nsew")

        lights_frame.grid_rowconfigure(0, weight=1)
        lights_frame.grid_columnconfigure(0, weight=1)
        lights_frame.grid_columnconfigure(1, weight=1)
        lights_frame.grid_columnconfigure(2, weight=1)

        temp_frame = tk.Frame(lights_frame)
        temp_frame.grid(row=0, column=0, sticky="nsew")
        temp_label = tk.Label(text="温控稳定", bg="grey")
        temp_label.place(in_=temp_frame, anchor="c", relx=0.5, rely=0.5)

        laser_frame = tk.Frame(lights_frame)
        laser_frame.grid(row=0, column=1, sticky="nsew")
        laser_label = tk.Label(text="激光器电流锁定", bg="grey")
        laser_label.place(in_=laser_frame, anchor="c", relx=0.5, rely=0.5)

        radio_frame = tk.Frame(lights_frame)
        radio_frame.grid(row=0, column=2, sticky="nsew")
        radio_label = tk.Label(text="射频频率锁定", bg="grey")
        radio_label.place(in_=radio_frame, anchor="c", relx=0.5, rely=0.5)

        indicator = Indicator(
            CLIENT,
            scheduler.get_scheduler(),
            root,
            temp_label,
            laser_label,
            radio_label,
        )

        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_rowconfigure(0, weight=1)
        buttons_frame.grid_rowconfigure(1, weight=1)
        buttons_frame.grid_rowconfigure(2, weight=1)
        buttons_frame.grid_rowconfigure(3, weight=1)

        # connect_button = tk.Button(buttons_frame, text="建立连接")
        # connect_button.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        start_button = tk.Button(buttons_frame, text="启动设备", command=start_device)
        start_button.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        temp_button = tk.Button(buttons_frame, text="启动加温", command=increase_temp)
        temp_button.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        lock_laser_button = tk.Button(buttons_frame, text="激光器电流锁定", command=lock_laser)
        lock_laser_button.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        start_dds_button = tk.Button(buttons_frame, text="DDS扫频", command=start_dds)
        start_dds_button.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)

        read_button_frame = tk.Frame(right_frame, width=30)
        read_button_frame.pack(fill="y", side=tk.LEFT)

        lowpass_cutoff_label = tk.Label(read_button_frame, text="低通滤波")
        lowpass_cutoff_label.pack()
        lowpass_cutoff_entry = tk.Entry(read_button_frame, width=20)
        lowpass_cutoff_entry.pack()

        highpass_cutoff_label = tk.Label(read_button_frame, text="高通滤波")
        highpass_cutoff_label.pack()
        highpass_cutoff_entry = tk.Entry(read_button_frame, width=20)
        highpass_cutoff_entry.pack()

        read_sin_button = tk.Button(
            read_button_frame,
            text="读取Sin",
            width=20,
            height=4,
            command=lambda: read_sin(custom_data),
        )
        read_sin_button.pack(padx=5, pady=5)

        read_sin_DDS = tk.Button(
            read_button_frame,
            text="读取DDS",
            width=20,
            height=4,
            command=lambda: read_dds(custom_data),
        )
        read_sin_DDS.pack(padx=5, pady=5)

        chart_download_frame = tk.Frame(right_frame, bg="green")
        chart_download_frame.pack(fill="both", side=tk.RIGHT, expand=True)

        # chart_download_frame.grid_columnconfigure(0, weight=1)
        # chart_download_frame.grid_rowconfigure(0, weight=6)
        # chart_download_frame.grid_rowconfigure(1, weight=6)
        # chart_download_frame.grid_rowconfigure(2, weight=1)

        time_chart_frame = tk.Frame(chart_download_frame, bg="blue")
        time_chart_frame.pack(side=tk.TOP, fill="both", expand=True)

        custom_data = CustomData(CLIENT)
        time_chart = FrameChart(
            custom_data,
            time_chart_frame,
            ChartMode.TIME,
            lowpass_cutoff_entry,
            highpass_cutoff_entry,
        )

        # Embed the plot in the frame
        # canvas = FigureCanvasTkAgg(time_chart.get_fig(), master=time_chart_frame)
        # canvas.draw()
        # canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        fft_chart_frame = tk.Frame(chart_download_frame, bg="green")
        fft_chart_frame.pack(side=tk.TOP, fill="both", expand=True)

        fft_chart = FrameChart(
            custom_data,
            fft_chart_frame,
            ChartMode.FFT,
            lowpass_cutoff_entry,
            highpass_cutoff_entry,
        )

        # download_frame = tk.Frame(chart_download_frame, height=10, pady=5)
        # download_frame.pack(side=tk.BOTTOM, fill="x")

        # download_button = tk.Button(download_frame, text="Download", width=10)
        # download_button.pack(side=tk.RIGHT)

        def on_closing():
            close(indicator, custom_data, time_chart, fft_chart, scheduler)
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)

        root.mainloop()
    finally:
        close(indicator, custom_data, time_chart, fft_chart, scheduler)


if __name__ == "__main__":
    main()
