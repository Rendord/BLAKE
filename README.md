# BLAKE

A Python tool for manga panel image processing. Features an interactive timeline-based GUI for experimenting with OpenCV image operations on JP2 manga panel images.

## Project Structure

```
BLAKE/
├── pyproject.toml           # Project config and dependencies (uv managed)
├── requirements.txt         # Frozen requirements
├── uv.lock                  # uv lockfile
├── libs/
│   └── vips-dev-8.18/       # Bundled libvips binaries (Windows, required by pyvips)
├── src/viewer/              # Main package
│   ├── __init__.py          # Auto-initializes libvips on Windows
│   ├── app.py               # Entry point (main() function)
│   ├── view.py              # UI components
│   ├── opencv_controller.py
│   ├── opencv_worker.py     # JP2 loading via pyvips
│   ├── operations.py        # Image operations
│   ├── panelsession.py
│   ├── cache.py
│   ├── types.py
│   └── geometry.py
├── manga_scans/
│   └── jp2/                 # 396 JP2 manga panel images (default image source)
└── util/                    # Utility scripts
```

## Setup

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
uv sync
```

This creates a virtual environment and installs all dependencies, including the `viewer` CLI entry point.

### libvips (required by pyvips)

pyvips requires the libvips C library to load JP2 images.

- **Windows**: Bundled at `libs/vips-dev-8.18/`. The package auto-adds it to the DLL search path on startup — no manual setup needed as long as the `libs/` directory is present.
- **macOS/Linux**: Install libvips via your package manager before running:
  ```bash
  # macOS
  brew install vips

  # Debian/Ubuntu
  sudo apt install libvips
  ```

## Usage

```bash
# Using the installed CLI entry point
uv run viewer

# Or run as a module from the project root
uv run python -m viewer.app
```

The application loads images from `manga_scans/jp2/` relative to the working directory.

### Keyboard Controls

| Key | Action |
|-----|--------|
| `+/=` | Apply selected operation |
| `-` | Delete operation |
| `Up` / `Down` | Navigate timeline (undo / redo) |
| `Left` / `Right` | Navigate panels |
| `Escape` | Close application |

### Available Operations

| Operation | Description |
|-----------|-------------|
| **Threshold** | Binary thresholding with adjustable value |
| **Morph Open** | Morphological opening — removes noise (erosion then dilation) |
| **Morph Close** | Morphological closing — fills holes (dilation then erosion) |
| **Invert** | Inverts grayscale values (black to white and vice versa) |

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| numpy | >=1.24.0 | Array operations |
| opencv-python | >=4.8.0 | Image processing |
| PyQt6 | >=6.6.0 | GUI |
| pyvips | >=3.1.1 | JP2 image loading |
| packaging | >=26.0 | Version utilities |
