import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-0.5, 0.5, 3000)

def square_fourier(x, N):
    y = np.zeros_like(x)
    for k in range(N):
        n = 2 * k + 1
        y += np.sin(n * x) / n
    return 4 / np.pi * y

plt.figure(figsize=(8, 5))

for N in [10, 50, 200]:
    plt.plot(x, square_fourier(x, N), label=f'N={N}')

plt.axhline(1, linestyle='--', linewidth=1, label='y=1')
plt.axhline(1.17898, linestyle=':', linewidth=1.5, label='Gibbs overshoot ≈ 1.17898')
plt.axvline(0, linestyle='--', linewidth=1)

plt.title('Gibbs Phenomenon near a Jump Discontinuity')
plt.xlabel('x')
plt.ylabel('S_N(x)')
plt.legend()
plt.grid(True)
plt.show()