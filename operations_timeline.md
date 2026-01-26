# Interactive Manga Panel Operation Timeline (Design Spec)

## Overview

Build an interactive Python 3.11 tool for experimenting with OpenCV image operations on manga panels.

The application consists of:

- A **main dynamic GUI** (PyQt preferred, Tkinter fallback) for:
  - viewing the current processed panel
  - selecting operations from a dropdown
  - editing operation parameters dynamically
  - navigating an operation timeline

- A **modal OpenCV comparison popup** that displays the last few timeline states side-by-side.

There is only ONE linear operation timeline (no branching, no A/B pipelines).

The OpenCV popup is purely for inspection and closes on the next keypress.

This is an MVP / experimental tool. Favor clarity and simplicity over abstraction.

---

## Libraries

- Python 3.11
- OpenCV (`cv2`)
- NumPy
- PyQt (preferred) or Tkinter if PyQt unavailable

OpenCV is used for image processing and the modal comparison window.

The main UI (dropdowns, inputs, preview) uses PyQt/Tkinter.

---

## Core Domain Model

### Operation (abstract)

Represents a single image operation.

Properties:
- `name: str`
- `params: dict[str, Any]`

Method:
- `apply(img: np.ndarray) -> np.ndarray`

Concrete MVP operations:

- Threshold (manual threshold parameter)
- Rotate (angle parameter; support ±1° and ±90°)
- MorphOpen (kernel size default 3x3)
- MorphClose (kernel size default 3x3)
- Invert

Each operation subclass defines:
- default params
- apply implementation

Operations should be immutable dataclasses where practical.

---

## PanelSession

Represents the current manga panel and its operation timeline.

Properties:
- `image_paths: list[Path]`
- `current_index: int`
- `original_image: np.ndarray`
- `operations: list[Operation]`
- `cursor: int` (0..len(operations))

Cursor semantics:
- The rendered image is produced by applying `operations[:cursor]` to `original_image`.

---

## Timeline Editing Rules

Insert at cursor:

When user presses `+`:

operations.insert(cursor, op)
cursor += 1

Undo / redo navigation:

- Up arrow: `cursor = max(0, cursor - 1)`
- Down arrow: `cursor = min(len(operations), cursor + 1)`

Delete current state:

Press `-`:
- If `cursor > 0`, delete `operations[cursor - 1]`
- Then `cursor -= 1`

Reset:

Press `r`:
- Clear operations
- Set cursor to 0

---

## Bounded History

Maintain at most:

- 50 operations in the past relative to cursor
- 50 operations in the future relative to cursor

After any modification:

Past trim:

If `cursor > 50`:
- drop `cursor - 50` ops from front
- adjust cursor accordingly

Future trim:

If `len(operations) - cursor > 50`:
- drop ops from the end

This keeps total operations bounded (~100 max).

---

## Rendering

Rendering is stateless:

- Always start from `original_image`
- Apply `operations[:cursor]` sequentially

No caching required for MVP.

---

## Main GUI Responsibilities

- Display current rendered image (single panel)
- Dropdown to select operation type
- Dynamic parameter inputs for selected operation
- Keyboard handling
- Display current file name and cursor position

Main UI Keybindings:

- `+` : apply selected operation at cursor
- `-` : delete last-applied operation at cursor
- Up arrow : move cursor backward
- Down arrow : move cursor forward
- Left arrow : previous manga panel (resets operations)
- Right arrow : next manga panel (resets operations)
- `r` : reset operations for current panel
- `c` : open side-by-side comparison view

---

## Side-by-Side Comparison View (OpenCV Popup)

Triggered by `c`.

Behavior:

- Generate up to 4 rendered stages ending at cursor:
  - states at: cursor-3, cursor-2, cursor-1, cursor (clamped to valid range)
- Each stage is rendered by applying `operations[:stage_cursor]`
- Resize images for display if needed
- Concatenate horizontally using `cv2.hconcat`
- Display using:

cv2.imshow("Compare", strip)
cv2.waitKey(0)
cv2.destroyWindow("Compare")

The comparison window is modal:
- closes on any keypress
- returns control to main GUI unchanged

This popup is NOT part of PyQt/Tkinter.

---

## Manga Folder Loading

- Load a directory of images (JP2/PNG/JPG).
- Sort filenames lexicographically.
- Start at first image.

On panel change:
- load new original image
- clear operations
- reset cursor

---

## Deliverables

- Single runnable entrypoint (e.g., app.py)
- Minimal README explaining how to run
- Clean readable code
- No overengineering

---

## Implementation Guidance

- Use Python list + cursor (not linked list)
- Keep everything simple
- Avoid observer patterns
- Avoid threading unless necessary
- GUI loop handles key events
- OpenCV compare window is blocking + modal

End of spec.
