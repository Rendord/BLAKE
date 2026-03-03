import os
import platform
from pathlib import Path
import ctypes

def _init_vips():
    if platform.system() == "Windows":
        # src/viewer/__init__.py -> src/viewer -> src -> root
        root = Path(__file__).resolve().parent.parent.parent
        vips_bin = root / "libs" / "vips-dev-8.18"
        vips_modules = vips_bin / "vips-modules-8.18"
        
        print('-------------------------------------------')
        print(vips_bin)
        print('-------------------------------------------')

        
        if vips_bin.exists():
            # This is the magic line for Python 3.8+ on Windows
            os.add_dll_directory(str(vips_bin))
            os.environ["PATH"] = str(vips_bin.resolve()) + os.pathsep + os.environ["PATH"]
        else:
            print(f"Warning: VIPS binaries not found at {vips_bin}")

_init_vips()