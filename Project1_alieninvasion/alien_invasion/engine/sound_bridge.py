"""sound_bridge.py — ctypes bridge to the C sound_core.dll library.

LANGUAGE: Python (ctypes FFI layer)
PURPOSE:  Calls native C functions for raw WAV sample buffer generation.
          Eliminates Python's per-sample function-call overhead (~100ns/call
          → ~2ns/call in C). For a 0.6s game-over at 22050Hz: 13,230 calls
          reduced from ~1.3ms to ~0.03ms.

The C library is compiled separately via build_engine.py using MinGW GCC.
If the DLL is not available, falls back to Python sound generation.
"""

import ctypes
import io
import os
import struct
import wave
from ctypes import POINTER, c_double, c_int, c_int16, c_uint, byref

# ── Sound type constants (must match sound_core.h) ──────────────
SOUND_TYPES = {
    'shoot': 0,
    'explosion': 1,
    'big_explosion': 2,
    'hit': 3,
    'powerup': 4,
    'level_up': 5,
    'game_over': 6,
    'combo': 7,
    'shield_break': 8,
}

# ── DLL loading ─────────────────────────────────────────────────
_lib = None
_lib_path = None


def _find_dll():
    """Locate the compiled sound_core DLL."""
    engine_dir = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.join(engine_dir, 'sound_core.dll')
    if os.path.exists(candidate):
        return candidate
    # Also check parent (in case it's in the package root)
    parent_candidate = os.path.join(
        os.path.dirname(engine_dir), 'engine', 'sound_core.dll')
    if os.path.exists(parent_candidate):
        return parent_candidate
    return None


def _load_lib():
    """Lazy-load the C library. Returns None if unavailable."""
    global _lib, _lib_path
    if _lib is not None:
        return _lib
    dll_path = _find_dll()
    if dll_path is None:
        return None
    try:
        _lib = ctypes.CDLL(dll_path)
        _lib_path = dll_path
        # Set function signatures
        _lib.generate_sound.argtypes = [c_int, c_int, POINTER(c_int)]
        _lib.generate_sound.restype = POINTER(c_int16)

        _lib.generate_shoot_custom.argtypes = [
            c_int, c_double, c_double, c_double, POINTER(c_int)]
        _lib.generate_shoot_custom.restype = POINTER(c_int16)

        _lib.generate_explosion_custom.argtypes = [
            c_int, c_double, c_double, c_uint, POINTER(c_int)]
        _lib.generate_explosion_custom.restype = POINTER(c_int16)

        _lib.free_buffer.argtypes = [POINTER(c_int16)]
        _lib.free_buffer.restype = None
        return _lib
    except OSError as e:
        print(f"[engine] Could not load sound_core.dll: {e}")
        return None


def is_c_available():
    """Check if the C sound library is available."""
    return _load_lib() is not None


def generate_sound_wav(sound_name, sample_rate=22050):
    """Generate a pygame Sound from the C library.

    Args:
        sound_name: One of the keys in SOUND_TYPES.
        sample_rate: Sample rate in Hz.

    Returns:
        pygame.mixer.Sound, or None on failure.
    """
    import pygame
    lib = _load_lib()
    if lib is None:
        return None

    sound_type = SOUND_TYPES.get(sound_name)
    if sound_type is None:
        return None

    n_samples = c_int(0)
    result = lib.generate_sound(sound_type, sample_rate, byref(n_samples))

    if not result or n_samples.value == 0:
        return None

    try:
        # Copy C buffer into Python bytes
        buffer_size = n_samples.value * 2  # 16-bit = 2 bytes per sample
        raw_bytes = ctypes.string_at(result, buffer_size)

        # Wrap in WAV format for pygame
        buf = io.BytesIO()
        with wave.open(buf, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(raw_bytes)
        buf.seek(0)
        return pygame.mixer.Sound(buf)
    finally:
        lib.free_buffer(result)
