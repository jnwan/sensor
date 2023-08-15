import numpy as np
import matplotlib.pyplot as plt

import logging

logger = logging.getLogger(__name__)

# 生成时域信号
Fs = 1000  # 采样率
t = np.linspace(0, 1, Fs, endpoint=False)  # 时间范围为0到1秒
f1 = 5  # 信号频率1
f2 = 50  # 信号频率2
signal = np.sin(2 * np.pi * f1 * t) + 0.5 * np.sin(2 * np.pi * f2 * t)

# 进行傅里叶变换
fft_result = np.fft.fft(signal)
freqs = np.fft.fftfreq(len(fft_result), 1 / Fs)

# 绘制时域信号
plt.subplot(2, 1, 1)
plt.plot(t, signal)
plt.title("Time Domain Signal")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")

# 绘制频域信号（傅里叶变换结果）
plt.subplot(2, 1, 2)
plt.plot(freqs, np.abs(fft_result))
plt.title("Frequency Domain Signal (Magnitude)")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")

plt.tight_layout()
plt.show()
