import numpy as np
import matplotlib.pyplot as plt

n = np.arange(1, 16)

flute_amp = 1 / n**2
violin_amp = 1 / n

plt.figure(figsize=(8, 5))

plt.plot(n, flute_amp, marker='o', label='Flute-like Spectrum')
plt.plot(n, violin_amp, marker='s', label='Violin-like Spectrum')

plt.title('Illustrative Harmonic Spectra of Flute and Violin')
plt.xlabel('Harmonic Number n')
plt.ylabel('Relative Amplitude')
plt.xticks(n)
plt.legend()
plt.grid(True)
plt.show()