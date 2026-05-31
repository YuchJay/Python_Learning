import numpy as np
import matplotlib.pyplot as plt

n = np.arange(1, 21)

square_amp = np.where(n % 2 == 1, 4 / (np.pi * n), 0)
saw_amp = 2 / n

plt.figure(figsize=(8, 5))

plt.bar(n - 0.2, square_amp, width=0.4, label='Square Wave')
plt.bar(n + 0.2, saw_amp, width=0.4, label='Sawtooth Wave')

plt.title('Harmonic Amplitudes of Square and Sawtooth Waves')
plt.xlabel('Harmonic Number n')
plt.ylabel('Amplitude')
plt.xticks(n)
plt.legend()
plt.grid(True, axis='y')
plt.show()