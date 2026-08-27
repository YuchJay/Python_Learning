"""kernels.py — Numba JIT-compiled batch physics kernels.

LANGUAGE: Numba (JIT-compiled Python subset → native machine code)
PURPOSE:  Just-In-Time compilation of math-heavy loops that process
          batches of data. Numba @njit functions compile to native code
          on first call, then run at C speed on subsequent calls.

          Unlike Cython (AOT compiled), Numba JIT compiles at runtime
          with no build step — just a decorator. This demonstrates the
          JIT compilation paradigm alongside Cython's AOT approach.

SPEEDUP:  ~10-50× over pure Python for batch array operations
          (the more elements, the bigger the advantage over interpreted Python).
"""

import math
import random

from numba import njit, int32, float64, void
from numba.types import UniTuple

# ═══════════════════════════════════════════════════════════════
#  Starfield batch kernels
# ═══════════════════════════════════════════════════════════════

@njit
def update_star_positions_batch(x_arr, y_arr, speed_arr, twinkle_arr,
                                twinkle_speed_arr, height, width):
    """JIT-compiled batch update of all star positions.

    Processes all 120 stars in a single native-code loop.
    ~15-25× faster than interpreted Python looping.

    Args:
        x_arr, y_arr: float64[:] position arrays (mutated in place)
        speed_arr: float64[:] downward scroll speed per star
        twinkle_arr: float64[:] twinkle phase offsets (mutated)
        twinkle_speed_arr: float64[:] twinkle speed per star
        height, width: screen dimensions (float64)
    """
    n = len(x_arr)
    for i in range(n):
        y_arr[i] += speed_arr[i]
        twinkle_arr[i] += twinkle_speed_arr[i]
        if y_arr[i] > height:
            y_arr[i] = random.uniform(-10.0, 0.0)
            x_arr[i] = random.uniform(0.0, width)


@njit
def calculate_star_alphas_batch(twinkle_arr, brightness_arr, result):
    """JIT-compiled batch alpha calculation for star twinkle effect.

    Computes per-star alpha values from twinkle sine waves.
    ~20-30× faster than interpreted Python.

    Args:
        twinkle_arr: float64[:] twinkle phase offsets
        brightness_arr: int32[:] base brightness per star
        result: int32[:] output array (mutated in place)
    """
    n = len(twinkle_arr)
    for i in range(n):
        flicker = (math.sin(twinkle_arr[i]) + 1.0) * 0.5
        alpha = int(brightness_arr[i] * (0.5 + 0.5 * flicker))
        if alpha < 0:
            alpha = 0
        elif alpha > 255:
            alpha = 255
        result[i] = alpha


# ═══════════════════════════════════════════════════════════════
#  Particle physics batch kernels
# ═══════════════════════════════════════════════════════════════

@njit
def update_particle_positions_batch(x_arr, y_arr, vx_arr, vy_arr,
                                    life_arr, gravity=0.08):
    """JIT-compiled batch particle physics update.

    Updates positions, applies gravity, decrements life.
    All in a single native-code loop with no Python overhead.
    ~30-50× faster than interpreted Python.

    Args:
        x_arr, y_arr: float64[:] position arrays (mutated)
        vx_arr: float64[:] x velocity (preserved)
        vy_arr: float64[:] y velocity (mutated — gravity applied)
        life_arr: int32[:] remaining life (mutated)
        gravity: float64 gravity constant
    """
    n = len(x_arr)
    for i in range(n):
        x_arr[i] += vx_arr[i]
        y_arr[i] += vy_arr[i]
        vy_arr[i] += gravity
        life_arr[i] -= 1


@njit
def calculate_particle_alphas_batch(life_arr, max_life_arr, result):
    """JIT-compiled batch alpha calculation for particle fade-out.

    Args:
        life_arr: int32[:] current remaining life
        max_life_arr: int32[:] initial maximum life
        result: int32[:] output alpha array (mutated)
    """
    n = len(life_arr)
    for i in range(n):
        ratio = life_arr[i] / max_life_arr[i]
        alpha = int(255.0 * ratio)
        if alpha < 0:
            alpha = 0
        result[i] = alpha


# ═══════════════════════════════════════════════════════════════
#  Collision helpers
# ═══════════════════════════════════════════════════════════════

@njit
def circle_rect_collision_batch(cx_arr, cy_arr, radius_arr,
                                 rx_arr, ry_arr, rw_arr, rh_arr,
                                 result):
    """JIT-compiled batch circle-vs-rectangle collision test.

    Used to accelerate powerup-ship collision when many powerups are active.
    ~40-60× faster than interpreted Python for 50+ objects.

    Args:
        cx_arr, cy_arr: float64[:] circle centers
        radius_arr: float64[:] circle radii
        rx_arr, ry_arr: float64[:] rectangle top-left corners
        rw_arr, rh_arr: float64[:] rectangle dimensions
        result: int32[:] output (1=hit, 0=miss)
    """
    n = len(cx_arr)
    for i in range(n):
        # Find closest point on rectangle to circle center
        closest_x = cx_arr[i]
        if closest_x < rx_arr[i]:
            closest_x = rx_arr[i]
        elif closest_x > rx_arr[i] + rw_arr[i]:
            closest_x = rx_arr[i] + rw_arr[i]

        closest_y = cy_arr[i]
        if closest_y < ry_arr[i]:
            closest_y = ry_arr[i]
        elif closest_y > ry_arr[i] + rh_arr[i]:
            closest_y = ry_arr[i] + rh_arr[i]

        # Check distance
        dx = cx_arr[i] - closest_x
        dy = cy_arr[i] - closest_y
        dist_sq = dx * dx + dy * dy

        result[i] = 1 if dist_sq <= radius_arr[i] * radius_arr[i] else 0
