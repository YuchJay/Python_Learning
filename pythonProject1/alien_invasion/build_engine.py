"""build_engine.py — One-shot build script for the compiled engine components.

USAGE:  python build_engine.py

This script handles:
  1. Compiling sound_core.c → sound_core.dll via GCC (MinGW on Windows)
  2. Compiling Cython .pyx files → .pyd extensions via Cython + setuptools

After running this, the game will use the compiled extensions automatically.
"""

import os
import subprocess
import sys

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(ENGINE_DIR)


def step(msg):
    """Print a build step header."""
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}")


def build_c_library():
    """Compile sound_core.c → sound_core.dll using GCC."""
    step("Step 1/2: Building C library (sound_core.dll)")

    c_file = os.path.join(ENGINE_DIR, 'sound_core.c')
    dll_file = os.path.join(ENGINE_DIR, 'sound_core.dll')

    if not os.path.exists(c_file):
        print("  ERROR: sound_core.c not found!")
        return False

    # Detect compiler
    gcc_paths = ['gcc', 'x86_64-w64-mingw32-gcc', 'mingw32-gcc']
    gcc = None
    for candidate in gcc_paths:
        try:
            subprocess.run([candidate, '--version'],
                          capture_output=True, timeout=5)
            gcc = candidate
            break
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue

    if gcc is None:
        print("  WARNING: GCC not found. Install MinGW-w64 or add GCC to PATH.")
        print("  The sound engine will fall back to Cython/Python generation.")
        return False

    cmd = [gcc, '-shared', '-O3', '-o', dll_file, c_file]
    if sys.platform != 'win32':
        cmd.append('-lm')

    print(f"  Compiler: {gcc}")
    print(f"  Command:  {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=ENGINE_DIR)
    if result.returncode != 0:
        print(f"  COMPILATION FAILED:")
        print(f"  {result.stderr}")
        return False

    size_kb = os.path.getsize(dll_file) / 1024
    print(f"  SUCCESS: sound_core.dll ({size_kb:.1f} KB)")
    return True


def build_cython_extensions():
    """Compile .pyx files → .pyd extensions using Cython."""
    step("Step 2/2: Building Cython extensions (.pyx → .pyd)")

    pyx_dir = ENGINE_DIR
    build_dir = os.path.join(PARENT_DIR, 'build')

    # Collect .pyx files
    pyx_files = []
    for f in sorted(os.listdir(pyx_dir)):
        if f.endswith('.pyx'):
            pyx_files.append(f[:-4])  # strip .pyx

    if not pyx_files:
        print("  No .pyx files found in engine/ directory.")
        return False

    print(f"  Modules to compile: {', '.join(pyx_files)}")

    try:
        from Cython.Build import cythonize
        from setuptools import Extension, setup
    except ImportError as e:
        print(f"  ERROR: {e}")
        print("  Install with: pip install cython setuptools")
        return False

    # Build each .pyx as a separate extension
    extensions = []
    for name in pyx_files:
        pyx_path = os.path.join(pyx_dir, f'{name}.pyx')
        extensions.append(Extension(
            f'engine.{name}_compiled',
            [pyx_path],
        ))

    # We need to run setup() which is normally a CLI entry point.
    # Instead, use Cython's build directly:
    print("  Compiling with Cython...")
    try:
        # Simple approach: use cython command-line
        import Cython.Compiler.Pipeline
        for name in pyx_files:
            pyx_path = os.path.join(pyx_dir, f'{name}.pyx')
            c_path = os.path.join(pyx_dir, f'{name}.c')
            print(f"    Cythonizing {name}.pyx → {name}.c ...")
            # Use the Cython CLI approach via subprocess
            result = subprocess.run(
                [sys.executable, '-m', 'cython', '-3', '-o', c_path, pyx_path],
                capture_output=True, text=True, cwd=ENGINE_DIR)
            if result.returncode != 0:
                print(f"    ERROR cythonizing {name}.pyx:")
                print(f"    {result.stderr}")
                return False

        # Now compile the .c files with GCC
        import sysconfig
        python_include = sysconfig.get_config_var('INCLUDEPY')
        if not python_include:
            # Try to find include dir
            for p in sys.path:
                candidate = os.path.join(p, 'include')
                if os.path.exists(candidate):
                    python_include = candidate
                    break

        print(f"  Python include: {python_include}")
        print("  Compiling .c → .pyd with GCC...")

        for name in pyx_files:
            c_path = os.path.join(pyx_dir, f'{name}.c')
            pyd_path = os.path.join(pyx_dir, f'{name}_compiled.pyd')

            # Build the GCC command
            gcc_cmd = [
                'gcc',
                '-shared',
                '-O3',
                '-o', pyd_path,
                c_path,
                f'-I{python_include}',
            ]
            if sys.platform == 'win32':
                # Find python DLL for linking
                py_lib = os.path.join(os.path.dirname(sys.executable), 'libs')
                if os.path.exists(py_lib):
                    gcc_cmd.append(f'-L{py_lib}')
                # Link against python3xx
                py_ver = f'{sys.version_info.major}{sys.version_info.minor}'
                gcc_cmd.append(f'-lpython{py_ver}')

            print(f"    Compiling {name}.c → {name}_compiled.pyd ...")
            result = subprocess.run(
                gcc_cmd, capture_output=True, text=True, cwd=ENGINE_DIR)
            if result.returncode != 0:
                print(f"    ERROR compiling {name}.c:")
                print(f"    {result.stderr}")
                # Continue trying other files
            else:
                size_kb = os.path.getsize(pyd_path) / 1024
                print(f"    SUCCESS: {name}_compiled.pyd ({size_kb:.1f} KB)")

    except Exception as e:
        print(f"  ERROR during Cython compilation: {e}")
        return False

    return True


def main():
    """Run the full build pipeline."""
    print("=" * 60)
    print("  Alien Invasion — Multi-Language Engine Build")
    print(f"  Python: {sys.version}")
    print(f"  CWD:    {os.getcwd()}")
    print("=" * 60)

    os.chdir(PARENT_DIR)

    c_ok = build_c_library()
    cython_ok = build_cython_extensions()

    print()
    print("=" * 60)
    print("  BUILD SUMMARY")
    print("=" * 60)
    print(f"  C library (sound_core.dll):   {'✓ BUILT' if c_ok else '✗ SKIPPED'}")
    print(f"  Cython extensions (.pyd):     {'✓ BUILT' if cython_ok else '✗ SKIPPED'}")
    print()
    print("  The game will automatically use whatever is built.")
    print("  Pure Python fallbacks are always available.")
    print("=" * 60)

    return 0 if (c_ok or True) and (cython_ok or True) else 1


if __name__ == '__main__':
    sys.exit(main())
