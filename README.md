# BLAKE!

A Python-based tool for manga panel image processing, featuring an interactive timeline-based operation tool for experimenting with OpenCV operations.

## Project Structure

```
BLAKE/
├── app.py                    # Interactive GUI application (PyQt6)
├── operations.py             # Operation class hierarchy
├── session.py               # Timeline management
├── geometry.py              # Geometric dataclasses
├── test_vectorization.py    # Image processing experiments
├── operations_timeline.md   # Design specification
├── requirements.txt         # Python dependencies
├── .venv/                   # Virtual environment (uv)
├── manga_scans/
│   └── jp2/                # Manga panel images (396 JP2 files)
├── src/                    # Source package (in development)
└── util/                   # Utility scripts
    └── rename.py           # File renaming utility
```

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Installation

#### Using uv (recommended)

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -r requirements.txt
```

#### Using pip

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Usage

#### Interactive Operations Tool

Run the interactive manga panel operation timeline tool:

```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows

# Run the application
python app.py

# Or specify custom image directory
python app.py /path/to/images
```

**Keyboard Controls:**
- `+` - Apply selected operation
- `-` - Delete operation (undo)
- `↑/↓` - Move cursor backward/forward (undo/redo)
- `←/→` - Navigate to previous/next manga panel
- `r` - Reset all operations
- `c` - Open side-by-side comparison view

**Available Operations:**
- **Threshold**: Binary thresholding (manual or OTSU)
- **Rotate**: Rotation with ±1° and ±90° quick buttons
- **MorphOpen**: Morphological opening (noise removal)
- **MorphClose**: Morphological closing (hole filling)
- **Invert**: Image inversion (black ↔ white)

The tool features a cursor-based timeline that allows you to apply operations, navigate through operation history, and compare different processing states side-by-side.

### Deactivating the Virtual Environment

When you're done working on the project:
```bash
deactivate
```

## Development

### Current Status

**✓ Interactive Operations Tool** - MVP complete with timeline-based operation management
- Cursor-based timeline with undo/redo
- 5 core image operations (Threshold, Rotate, Morph Open/Close, Invert)
- Side-by-side comparison view
- Bounded history (50 ops past/future)
- Keyboard-driven workflow

**In Progress** - Manga panel vectorization pipeline

### Dependencies

- Python 3.11+
- NumPy ≥1.24.0
- OpenCV ≥4.8.0
- PyQt6 ≥6.6.0
- Pillow ≥10.0.0

### Design Documentation

See `operations_timeline.md` for the complete design specification of the interactive operations tool.
