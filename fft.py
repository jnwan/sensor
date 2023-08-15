import numpy as np
import matplotlib.pyplot as plt

import logging

logger = logging.getLogger(__name__)


def fft(data, fs):
    fft = np.fft.fftshift(np.fft.fft(data))  # 双边谱离散傅里叶变换，得到复数数组

    # 双边谱傅里叶变换的横轴（频率，Hz）
    f = np.arange(-len(data) // 2, len(data) // 2) * (fs / len(data))

    cali_fft = np.abs(fft) * 2 / len(data)  # 强度标定的傅里叶变换幅度谱

    return (f[f >= 0], cali_fft[f >= 0])


def filter(data, fs, lowpass_cutoff, highpass_cutoff):
    fft = np.fft.fftshift(np.fft.fft(data))  # Shifted double-sided FFT

    f = np.arange(-len(data) // 2, len(data) // 2) * (fs / len(data))  # Frequency axis

    if lowpass_cutoff and lowpass_cutoff.isdigit():
        fft[
            np.abs(f) > int(lowpass_cutoff)
        ] = 0  # Low-pass filter: Set frequencies greater than b to zero
    if highpass_cutoff and highpass_cutoff.isdigit():
        fft[
            np.logical_and(f < int(highpass_cutoff), f > -int(highpass_cutoff))
        ] = 0  # High-pass filter: Set frequencies between a and -a to zero

    return np.fft.ifft(
        np.fft.ifftshift(fft)
    )  # Inverse FFT to obtain filtered time-domain signal


if __name__ == "__main__":
    # 生成示例信号
    fs = 1000  # 采样频率
    t = np.arange(0, 1, 1 / fs)  # 时间序列
    f1 = 5  # 低频信号频率
    f2 = 50  # 高频信号频率
    signal = (
        np.sin(2 * np.pi * f1 * t)
        + 0.5 * np.sin(2 * np.pi * f2 * t)
        + np.random.normal(0, 0.5, len(t))
    )

    # 选择滤波器截止频率和阶数
    lowpass_cutoff = 30  # 低通截止频率
    highpass_cutoff = 10  # 高通截止频率
    filter_order = 6  # 滤波器阶数

    filtered = filter(
        signal,
        fs,
        lowpass_cutoff,
        highpass_cutoff,
    )

    # 绘制原始信号、低通滤波后的信号和高通滤波后的信号
    plt.figure(figsize=(10, 6))
    plt.plot(t, signal, label="Origin")
    plt.plot(t, filtered, label="Filtered")
    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.legend()
    plt.grid()
    plt.show()
