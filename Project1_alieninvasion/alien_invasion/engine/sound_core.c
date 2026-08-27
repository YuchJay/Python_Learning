/* sound_core.c — Native C WAV sample buffer generation
 *
 * Each generate_* function creates the entire sample buffer in a single tight
 * C loop, avoiding the ~100ns per-sample Python function-call overhead.
 * For a 0.6s game-over sound at 22050Hz, that's 13,230 Python calls saved.
 */

#include "sound_core.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* ── Internal: simple LCG random for noise-based effects ─────── */
static unsigned int _rand_state = 42;

static void _seed_rand(unsigned int seed) {
    _rand_state = seed;
}

static double _rand_double(void) {
    _rand_state = _rand_state * 1103515245u + 12345u;
    return (double)(_rand_state & 0x7FFFFFFF) / 2147483647.0;
}

/* ── Helper: write sample with envelope ─────────────────────── */
static inline int16_t _sample(double val, double envelope) {
    double v = val * envelope;
    if (v > 1.0) v = 1.0;
    if (v < -1.0) v = -1.0;
    return (int16_t)(v * 32767.0);
}

/* ═══════════════════════════════════════════════════════════════
 *  Sound generators
 * ═══════════════════════════════════════════════════════════════ */

static int16_t* _gen_shoot(int rate, int* n) {
    double duration = 0.08;
    *n = (int)(rate * duration);
    int16_t* buf = (int16_t*)malloc(*n * sizeof(int16_t));
    if (!buf) return NULL;
    for (int i = 0; i < *n; i++) {
        double t = (double)i / rate;
        double env = 1.0 - (double)i / *n;
        double freq = 800.0 + 2000.0 * t / 0.08;
        buf[i] = _sample(sin(2.0 * M_PI * freq * t) * 0.3, env);
    }
    return buf;
}

static int16_t* _gen_explosion(int rate, int* n) {
    double duration = 0.18;
    *n = (int)(rate * duration);
    int16_t* buf = (int16_t*)malloc(*n * sizeof(int16_t));
    if (!buf) return NULL;
    for (int i = 0; i < *n; i++) {
        double env = 1.0 - (double)i / *n;
        double noise = (_rand_double() * 2.0 - 1.0) * 0.35;
        buf[i] = _sample(noise, env);
    }
    return buf;
}

static int16_t* _gen_big_explosion(int rate, int* n) {
    double duration = 0.35;
    *n = (int)(rate * duration);
    int16_t* buf = (int16_t*)malloc(*n * sizeof(int16_t));
    if (!buf) return NULL;
    for (int i = 0; i < *n; i++) {
        double t = (double)i / rate;
        double env = 1.0 - (double)i / *n;
        double noise = (_rand_double() * 2.0 - 1.0) * 0.4;
        double rumble = sin(2.0 * M_PI * 60.0 * t) * 0.5;
        buf[i] = _sample(noise * 0.7 + rumble * 0.3, env);
    }
    return buf;
}

static int16_t* _gen_hit(int rate, int* n) {
    double duration = 0.25;
    *n = (int)(rate * duration);
    int16_t* buf = (int16_t*)malloc(*n * sizeof(int16_t));
    if (!buf) return NULL;
    for (int i = 0; i < *n; i++) {
        double t = (double)i / rate;
        double env = 1.0 - (double)i / *n;
        buf[i] = _sample(sin(2.0 * M_PI * 150.0 * t) * 0.5, env);
    }
    return buf;
}

static int16_t* _gen_powerup(int rate, int* n) {
    double duration = 0.24;
    *n = (int)(rate * duration);
    int16_t* buf = (int16_t*)malloc(*n * sizeof(int16_t));
    if (!buf) return NULL;
    for (int i = 0; i < *n; i++) {
        double t = (double)i / rate;
        double env = 1.0 - (double)i / *n;
        double freq;
        if (t < 0.08)      freq = 600.0;
        else if (t < 0.16) freq = 900.0;
        else               freq = 1200.0;
        buf[i] = _sample(sin(2.0 * M_PI * freq * t) * 0.3, env);
    }
    return buf;
}

static int16_t* _gen_level_up(int rate, int* n) {
    double duration = 0.40;
    *n = (int)(rate * duration);
    int16_t* buf = (int16_t*)malloc(*n * sizeof(int16_t));
    if (!buf) return NULL;
    for (int i = 0; i < *n; i++) {
        double t = (double)i / rate;
        double env = 1.0 - (double)i / *n;
        double freq;
        if (t < 0.10)      freq = 523.0;   /* C5 */
        else if (t < 0.20) freq = 659.0;   /* E5 */
        else if (t < 0.30) freq = 784.0;   /* G5 */
        else               freq = 1047.0;  /* C6 */
        buf[i] = _sample(sin(2.0 * M_PI * freq * t) * 0.3, env);
    }
    return buf;
}

static int16_t* _gen_game_over(int rate, int* n) {
    double duration = 0.60;
    *n = (int)(rate * duration);
    int16_t* buf = (int16_t*)malloc(*n * sizeof(int16_t));
    if (!buf) return NULL;
    for (int i = 0; i < *n; i++) {
        double t = (double)i / rate;
        double env = 1.0 - (double)i / *n;
        double freq;
        if (t < 0.15)      freq = 440.0;
        else if (t < 0.30) freq = 370.0;
        else if (t < 0.45) freq = 311.0;
        else               freq = 262.0;
        buf[i] = _sample(sin(2.0 * M_PI * freq * t) * 0.35, env);
    }
    return buf;
}

static int16_t* _gen_combo(int rate, int* n) {
    double duration = 0.10;
    *n = (int)(rate * duration);
    int16_t* buf = (int16_t*)malloc(*n * sizeof(int16_t));
    if (!buf) return NULL;
    for (int i = 0; i < *n; i++) {
        double t = (double)i / rate;
        double env = 1.0 - (double)i / *n;
        buf[i] = _sample(sin(2.0 * M_PI * 1200.0 * t) * 0.25, env);
    }
    return buf;
}

static int16_t* _gen_shield_break(int rate, int* n) {
    double duration = 0.12;
    *n = (int)(rate * duration);
    int16_t* buf = (int16_t*)malloc(*n * sizeof(int16_t));
    if (!buf) return NULL;
    for (int i = 0; i < *n; i++) {
        double env = 1.0 - (double)i / *n;
        double noise = (_rand_double() * 2.0 - 1.0) * 0.3;
        buf[i] = _sample(noise, env);
    }
    return buf;
}

/* ═══════════════════════════════════════════════════════════════
 *  Public API
 * ═══════════════════════════════════════════════════════════════ */

DLL_EXPORT int16_t* generate_sound(int sound_type, int sample_rate, int* n_samples) {
    _seed_rand((unsigned int)sample_rate ^ (unsigned int)sound_type);
    switch (sound_type) {
        case SOUND_SHOOT:        return _gen_shoot(sample_rate, n_samples);
        case SOUND_EXPLOSION:    return _gen_explosion(sample_rate, n_samples);
        case SOUND_BIG_EXPLOSION:return _gen_big_explosion(sample_rate, n_samples);
        case SOUND_HIT:          return _gen_hit(sample_rate, n_samples);
        case SOUND_POWERUP:      return _gen_powerup(sample_rate, n_samples);
        case SOUND_LEVEL_UP:     return _gen_level_up(sample_rate, n_samples);
        case SOUND_GAME_OVER:    return _gen_game_over(sample_rate, n_samples);
        case SOUND_COMBO:        return _gen_combo(sample_rate, n_samples);
        case SOUND_SHIELD_BREAK: return _gen_shield_break(sample_rate, n_samples);
        default:                 return NULL;
    }
}

DLL_EXPORT int16_t* generate_shoot_custom(int rate, double f_start, double f_end,
                                          double duration, int* n) {
    *n = (int)(rate * duration);
    int16_t* buf = (int16_t*)malloc(*n * sizeof(int16_t));
    if (!buf) return NULL;
    for (int i = 0; i < *n; i++) {
        double t = (double)i / rate;
        double env = 1.0 - (double)i / *n;
        double frac = (duration > 0.001) ? t / duration : 1.0;
        double freq = f_start + (f_end - f_start) * frac;
        buf[i] = _sample(sin(2.0 * M_PI * freq * t) * 0.3, env);
    }
    return buf;
}

DLL_EXPORT int16_t* generate_explosion_custom(int rate, double duration,
                                              double amplitude, unsigned int seed,
                                              int* n) {
    _seed_rand(seed);
    *n = (int)(rate * duration);
    int16_t* buf = (int16_t*)malloc(*n * sizeof(int16_t));
    if (!buf) return NULL;
    for (int i = 0; i < *n; i++) {
        double env = 1.0 - (double)i / *n;
        double noise = (_rand_double() * 2.0 - 1.0) * amplitude;
        buf[i] = _sample(noise, env);
    }
    return buf;
}

DLL_EXPORT void free_buffer(int16_t* buf) {
    free(buf);
}
