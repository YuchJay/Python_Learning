/* sound_core.h — C-level WAV sample buffer generation
 *
 * LANGUAGE: C (native, compiled to shared library)
 * PURPOSE:  Raw PCM sample generation — the tightest loop in the game.
 *           Python's per-sample function call overhead (~100ns per call)
 *           adds up to 2-5ms per sound effect; C eliminates this.
 *
 * USAGE:    Compiled to sound_core.dll via MinGW GCC, called from Python
 *           via ctypes in sound_bridge.py.
 */

#ifndef SOUND_CORE_H
#define SOUND_CORE_H

#include <stdint.h>

#ifdef _WIN32
    #define DLL_EXPORT __declspec(dllexport)
#else
    #define DLL_EXPORT
#endif

/* Sound effect type identifiers */
#define SOUND_SHOOT        0
#define SOUND_EXPLOSION    1
#define SOUND_BIG_EXPLOSION 2
#define SOUND_HIT          3
#define SOUND_POWERUP      4
#define SOUND_LEVEL_UP     5
#define SOUND_GAME_OVER    6
#define SOUND_COMBO        7
#define SOUND_SHIELD_BREAK 8

/**
 * Generate a complete 16-bit mono WAV sample buffer for a given sound effect.
 *
 * @param sound_type   One of the SOUND_* constants above.
 * @param sample_rate  Sample rate in Hz (e.g. 22050).
 * @param n_samples    [out] Number of samples generated.
 * @return             Heap-allocated int16_t buffer; caller must free_buffer().
 */
DLL_EXPORT int16_t* generate_sound(int sound_type, int sample_rate, int* n_samples);

/**
 * Generate shoot sound with configurable parameters.
 * @param freq_start   Start frequency (Hz)
 * @param freq_end     End frequency (Hz)
 * @param duration     Duration in seconds
 */
DLL_EXPORT int16_t* generate_shoot_custom(int sample_rate, double freq_start,
                                          double freq_end, double duration,
                                          int* n_samples);

/**
 * Generate explosion sound (white noise).
 * @param duration     Duration in seconds
 * @param amplitude    Volume 0.0-1.0
 * @param seed         RNG seed for reproducibility
 */
DLL_EXPORT int16_t* generate_explosion_custom(int sample_rate, double duration,
                                              double amplitude, unsigned int seed,
                                              int* n_samples);

/**
 * Free a buffer previously returned by generate_sound() or generate_*_custom().
 */
DLL_EXPORT void free_buffer(int16_t* buf);

#endif /* SOUND_CORE_H */
