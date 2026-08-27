"""engine/__init__.py — Multi-language engine package with smart imports.

ARCHITECTURE:
  This package provides a unified interface to the game's performance-
  critical subsystems. Each subsystem can be served by one of several
  backends:

  ┌─────────────────┬──────────────────┬───────────────────┬─────────────────┐
  │ Subsystem       │ Language 1       │ Language 2        │ Language 3      │
  ├─────────────────┼──────────────────┼───────────────────┼─────────────────┤
  │ Starfield       │ Python (original)│ Cython (.pyx→.pyd)│                 │
  │ Explosion       │ Python (original)│ Cython (.pyx→.pyd)│                 │
  │ Sound           │ Python (original)│ Cython (.pyx→.pyd)│ C (.dll via FFI) │
  │ Physics Kernels │ Python           │ Numba (@njit JIT) │                 │
  └─────────────────┴──────────────────┴───────────────────┴─────────────────┘

  Priority: Compiled extension → Python fallback (always works)
"""

# Ensure the engine directory is available for sub-module imports
# (needed by Cython modules compiled via pyximport, which doesn't
# automatically add the source directory to sys.path)
import os as _os
import sys as _sys
_ENGINE_DIR = _os.path.dirname(_os.path.abspath(__file__))
if _ENGINE_DIR not in _sys.path:
    _sys.path.insert(0, _ENGINE_DIR)

# ═══════════════════════════════════════════════════════════════
#  Starfield Engine
# ═══════════════════════════════════════════════════════════════

StarfieldEngine = None
_starfield_source = 'python (fallback)'

# 1) Try compiled Cython extension (.pyd)
try:
    from engine.starfield_compiled import StarfieldEngine as _SFE_Cython
    StarfieldEngine = _SFE_Cython
    _starfield_source = 'cython (AOT compiled)'
except ImportError:
    pass

# 2) Try pyximport (on-the-fly Cython compilation)
if StarfieldEngine is None:
    try:
        import pyximport
        pyximport.install(language_level=3)
        from engine.starfield import StarfieldEngine as _SFE_pyx
        StarfieldEngine = _SFE_pyx
        _starfield_source = 'cython (pyximport JIT)'
    except (ImportError, Exception):
        pass

# 3) Fallback to pure Python
if StarfieldEngine is None:
    from starfield import Starfield as StarfieldEngine
    _starfield_source = 'python (original)'

# ═══════════════════════════════════════════════════════════════
#  Explosion Engine
# ═══════════════════════════════════════════════════════════════

ExplosionParticle = None
create_explosion = None
_explosion_source = 'python (fallback)'

# 1) Try compiled Cython extension
try:
    from engine.explosion_compiled import Particle as _EP_Cython
    from engine.explosion_compiled import create_explosion as _CE_Cython
    ExplosionParticle = _EP_Cython
    create_explosion = _CE_Cython
    _explosion_source = 'cython (AOT compiled)'
except ImportError:
    pass

# 2) Try pyximport
if ExplosionParticle is None:
    try:
        import pyximport
        pyximport.install(language_level=3)
        from engine.explosion import Particle as _EP_pyx
        from engine.explosion import create_explosion as _CE_pyx
        ExplosionParticle = _EP_pyx
        create_explosion = _CE_pyx
        _explosion_source = 'cython (pyximport JIT)'
    except (ImportError, Exception):
        pass

# 3) Fallback to pure Python
if ExplosionParticle is None:
    from explosion import Particle as ExplosionParticle

# ═══════════════════════════════════════════════════════════════
#  Sound Engine
# ═══════════════════════════════════════════════════════════════

SoundEngine = None
_sound_source = 'python (fallback)'

# 1) Try compiled Cython extension
try:
    from engine.sound_compiled import SoundEngine as _SE_Cython
    SoundEngine = _SE_Cython
    _sound_source = 'cython (AOT compiled) + C DLL'
except ImportError:
    pass

# 2) Try pyximport
if SoundEngine is None:
    try:
        import pyximport
        pyximport.install(language_level=3)
        from engine.sound import SoundEngine as _SE_pyx
        SoundEngine = _SE_pyx
        # Check if C library was also loaded inside the Cython module
        try:
            from engine.sound import _c_available as _cy_sound_c
            if _cy_sound_c:
                _sound_source = 'cython (JIT) + C DLL'
            else:
                _sound_source = 'cython (pyximport JIT)'
        except ImportError:
            _sound_source = 'cython (pyximport JIT)'
    except (ImportError, Exception):
        pass

# 3) Fallback to pure Python
if SoundEngine is None:
    from sound_manager import SoundManager as SoundEngine
    _sound_source = 'python (original)'

# ═══════════════════════════════════════════════════════════════
#  Numba physics kernels
# ═══════════════════════════════════════════════════════════════

kernels = None
_kernels_source = 'unavailable'

try:
    from engine.kernels import (
        update_star_positions_batch,
        calculate_star_alphas_batch,
        update_particle_positions_batch,
        calculate_particle_alphas_batch,
        circle_rect_collision_batch,
    )
    kernels = {
        'update_star_positions': update_star_positions_batch,
        'calculate_star_alphas': calculate_star_alphas_batch,
        'update_particle_positions': update_particle_positions_batch,
        'calculate_particle_alphas': calculate_particle_alphas_batch,
        'circle_rect_collision': circle_rect_collision_batch,
    }
    _kernels_source = 'numba (JIT compiled)'
except ImportError:
    pass


# ═══════════════════════════════════════════════════════════════
#  Status reporting
# ═══════════════════════════════════════════════════════════════

def get_engine_status():
    """Return a dict describing which backend each subsystem is using.

    Call after imports to verify the multi-language architecture is active.
    """
    return {
        'starfield': _starfield_source,
        'explosion': _explosion_source,
        'sound': _sound_source,
        'kernels': _kernels_source,
    }


def print_engine_status():
    """Print a formatted table of engine backend statuses."""
    status = get_engine_status()
    print("=" * 55)
    print("  ENGINE STATUS — Multi-Language Architecture")
    print("=" * 55)
    labels = {
        'starfield': 'Starfield Renderer',
        'explosion': 'Particle System',
        'sound': 'Sound Synthesis',
        'kernels':  'Physics Kernels',
    }
    for key, label in labels.items():
        src = status[key]
        # Color-code by language
        if 'C DLL' in src or 'AOT' in src:
            tag = '[C + Cython]'
        elif 'cython' in src:
            tag = '[Cython]'
        elif 'numba' in src:
            tag = '[Numba JIT]'
        elif 'original' in src:
            tag = '[Python]'
        else:
            tag = '[---]'
        print(f"  {label:<22} {tag:<14} ({src})")
    print("=" * 55)


# Auto-report on first import (can be silenced with ENGINE_QUIET=1)
import os as _os
if not _os.environ.get('ENGINE_QUIET'):
    # Defer print to allow pygame init first
    pass  # print_engine_status() is called explicitly from main.py
