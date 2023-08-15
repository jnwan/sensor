import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from connect import scan_ports_and_connect, connect_port
from indicator import Indicator
from data_api import write_modbus
from config import ConfigSingleton
from custom_data import CustomData, DataMode
from frame_chart import TimeChart, FFTChart
from scheduler import Scheduler
import customtkinter
import logging

logging.basicConfig(
    level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Set the log message format
    handlers=[
        logging.FileHandler("app.log"),  # Log to a file
        logging.StreamHandler(),  # Log to the console
    ],
)

logger = logging.getLogger(__name__)

CONFIG = None
CLIENT = None


def close(
    indicator: Indicator,
    custom_data: CustomData,
    time_chart: TimeChart,
    fft_chart: FFTChart,
    scheduler: Scheduler,
):
    logger.info("Closing App...")
    custom_data.stop()
    logger.info("Chart data refresh stopped")
    time_chart.stop()
    logger.info("Time chart closed")
    fft_chart.stop()
    logger.info("FFT chart closed")
    indicator.stop()
    logger.info("Indicator refresh stopped")
    scheduler.stop()
    logger.info("Scheduled stopped")


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
DEVICE_PORT = ConfigSingleton().get_config()["DEVICE_PORT"]


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
    if DEVICE_PORT:
        CLIENT = connect_port(DEVICE_PORT)
        assert CLIENT is not None, f"Can't connect to port {DEVICE_PORT}"
    else:
        clients = scan_ports_and_connect()
        assert len(clients) == 1, "Can't find proper port to connect"
        CLIENT = clients[0]

    try:
        root = customtkinter.CTk()
        root.geometry("1920x1080")  # Set the size of the window

        scheduler = Scheduler()

        # Create two frames for the sections
        left_frame = customtkinter.CTkFrame(root)  # First section with 1/3 width
        right_frame = customtkinter.CTkFrame(root)  # Second section with 2/3 width

        # Define the grid layout
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=6)

        # Place the frames on the grid
        left_frame.grid(row=0, column=0, sticky="nsew")
        right_frame.grid(row=0, column=1, sticky="nsew")

        lights_frame = customtkinter.CTkFrame(left_frame)
        buttons_frame = customtkinter.CTkFrame(left_frame)

        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=6)

        lights_frame.grid(row=0, column=0, sticky="nsew")
        buttons_frame.grid(row=1, column=0, sticky="nsew")

        lights_frame.grid_rowconfigure(0, weight=1)
        lights_frame.grid_columnconfigure(0, weight=1)
        lights_frame.grid_columnconfigure(1, weight=1)
        lights_frame.grid_columnconfigure(2, weight=1)

        temp_frame = customtkinter.CTkFrame(lights_frame)
        temp_frame.grid(row=0, column=0, sticky="nsew")
        temp_label = customtkinter.CTkLabel(temp_frame, text="温控稳定", fg_color="grey")
        temp_label.place(in_=temp_frame, anchor="c", relx=0.5, rely=0.5)

        laser_frame = customtkinter.CTkFrame(lights_frame)
        laser_frame.grid(row=0, column=1, sticky="nsew")
        laser_label = customtkinter.CTkLabel(
            laser_frame, text="激光器电流锁定", fg_color="grey"
        )
        laser_label.place(in_=laser_frame, anchor="c", relx=0.5, rely=0.5)

        radio_frame = customtkinter.CTkFrame(lights_frame)
        radio_frame.grid(row=0, column=2, sticky="nsew")
        radio_label = customtkinter.CTkLabel(
            radio_frame, text="射频频率锁定", fg_color="grey"
        )
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

        # connect_button = customtkinter.CTkButton(buttons_frame, text="建立连接")
        # connect_button.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        start_button = customtkinter.CTkButton(
            buttons_frame, text="启动设备", command=start_device
        )
        start_button.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        temp_button = customtkinter.CTkButton(
            buttons_frame, text="启动加温", command=increase_temp
        )
        temp_button.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        lock_laser_button = customtkinter.CTkButton(
            buttons_frame, text="激光器电流锁定", command=lock_laser
        )
        lock_laser_button.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        start_dds_button = customtkinter.CTkButton(
            buttons_frame, text="DDS扫频", command=start_dds
        )
        start_dds_button.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)

        read_button_frame = customtkinter.CTkFrame(right_frame, width=50)
        read_button_frame.pack(fill="both", side=tk.LEFT)

        lowpass_cutoff_label = customtkinter.CTkLabel(read_button_frame, text="低通滤波")
        lowpass_cutoff_label.pack()
        lowpass_cutoff_entry = customtkinter.CTkEntry(read_button_frame, width=20)
        lowpass_cutoff_entry.pack(fill="both")

        highpass_cutoff_label = customtkinter.CTkLabel(read_button_frame, text="高通滤波")
        highpass_cutoff_label.pack()
        highpass_cutoff_entry = customtkinter.CTkEntry(read_button_frame, width=20)
        highpass_cutoff_entry.pack(fill="both")

        read_sin_button = customtkinter.CTkButton(
            read_button_frame,
            text="读取Sin",
            width=40,
            height=6,
            command=lambda: read_sin(custom_data),
        )
        read_sin_button.pack(padx=5, pady=5)

        read_sin_DDS = customtkinter.CTkButton(
            read_button_frame,
            text="读取DDS",
            width=40,
            height=6,
            command=lambda: read_dds(custom_data),
        )
        read_sin_DDS.pack(padx=5, pady=5)

        custom_data = CustomData(CLIENT, scheduler.get_scheduler())

        download_on = customtkinter.StringVar(value="off")
        download_switch = customtkinter.CTkSwitch(
            read_button_frame,
            width=40,
            height=6,
            text="下载",
            command=lambda: custom_data.set_download(download_on.get() == "on"),
            variable=download_on,
            onvalue="on",
            offvalue="off",
        )
        download_switch.pack(padx=5, pady=5, fill="x")

        chart_download_frame = customtkinter.CTkFrame(right_frame)
        chart_download_frame.pack(fill="both", side=tk.RIGHT, expand=True)

        # chart_download_frame.grid_columnconfigure(0, weight=1)
        # chart_download_frame.grid_rowconfigure(0, weight=6)
        # chart_download_frame.grid_rowconfigure(1, weight=6)
        # chart_download_frame.grid_rowconfigure(2, weight=1)

        time_chart_frame = customtkinter.CTkFrame(chart_download_frame)
        time_chart_frame.pack(side=tk.TOP, fill="both", expand=True)

        time_chart = TimeChart(
            custom_data,
            time_chart_frame,
            lowpass_cutoff_entry,
            highpass_cutoff_entry,
        )

        # Embed the plot in the frame
        # canvas = FigureCanvasTkAgg(time_chart.get_fig(), master=time_chart_frame)
        # canvas.draw()
        # canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        fft_chart_frame = customtkinter.CTkFrame(chart_download_frame)
        fft_chart_frame.pack(side=tk.TOP, fill="both", expand=True)

        fft_chart = FFTChart(
            custom_data,
            fft_chart_frame,
        )

        # download_frame = customtkinter.CTkFrame(chart_download_frame)
        # download_frame.pack(side=customtkinter.BOTTOM, fill="x")

        # download_button = customtkinter.CTkButton(
        #     download_frame, text="Download", width=10
        # )
        # download_button.pack(side=customtkinter.RIGHT)

        def on_closing():
            close(indicator, custom_data, time_chart, fft_chart, scheduler)
            root.destroy()
            root.quit()

        root.protocol("WM_DELETE_WINDOW", on_closing)

        root.mainloop()
    except:
        close(indicator, custom_data, time_chart, fft_chart, scheduler)


if __name__ == "__main__":
    main()
