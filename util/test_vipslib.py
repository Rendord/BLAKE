import pyvips
from pyvips import ffi

# Access the underlying C library directly
vips_lib = pyvips.vips_lib

# Call the C function 'vips_config'
config_ptr = vips_lib.vips_config()
config_str = ffi.string(config_ptr).decode()

print("--- VIPS COMPILE-TIME CONFIG ---")
print(f"JPEG 2000 (OpenJPEG): {'openjpeg' in config_str.lower()}")
print(f"TIFF:                {'tiff' in config_str.lower()}")
print(f"WebP:                {'webp' in config_str.lower()}")
print("-" * 30)

# Check for the actual 'jp2kload' operation in the registry
has_jp2 = vips_lib.vips_type_find("VipsOperation", "jp2kload") != 0
print(f"Does the 'jp2kload' operation exist? {has_jp2}")
