import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-np.pi, np.pi, 2000)

def sawtooth_fourier(x, N):
    y = np.zeros_like(x)
    for n in range(1, N + 1):
        y += ((-1) ** (n + 1)) * np.sin(n * x) / n
    return 2 * y

plt.figure(figsize=(8, 5))

for N in [1, 5, 20, 100]:
    plt.plot(x, sawtooth_fourier(x, N), label=f'N={N}')

plt.plot(x, x, linestyle='--', linewidth=1, label='f(x)=x')

plt.title('Fourier Approximation of Sawtooth Wave')
plt.xlabel('x')
plt.ylabel('S_N(x)')
plt.legend()
plt.grid(True)
plt.show()