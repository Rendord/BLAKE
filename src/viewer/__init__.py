import os
import platform
from pathlib import Path
import ctypes

def _init_vips():
    os_environment = platform.system()

    if os_environment == "Windows":
        # src/viewer/__init__.py -> src/viewer -> src -> root
        root = Path(__file__).resolve().parent.parent.parent
        vips_bin = root / "libs" / "vips-dev-8.18"
        vips_modules = vips_bin / "vips-modules-8.18"
        
        print('-------------------------------------------')
        print("binary_path: " + vips_bin)
        print('-------------------------------------------')

        
        if vips_bin.exists():
            # This is the magic line for Python 3.8+ on Windows
            os.add_dll_directory(str(vips_bin))
            os.environ["PATH"] = str(vips_bin.resolve()) + os.pathsep + os.environ["PATH"]
        else:
            print(f"Warning: VIPS binaries not found at {vips_bin}")

    elif os_environment == "Darwin":
        # Inject Homebrew's lib path into the fallback dynamic linker path
        brew_lib = "/opt/homebrew/lib"
        current_dyld = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
        if brew_lib not in current_dyld:
            os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = f"{brew_lib}:{current_dyld}".strip(":")

_init_vips()