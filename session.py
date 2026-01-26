"""
PanelSession class for managing manga panel operations timeline.

Handles:
- Loading and navigating between manga panels
- Operation timeline with cursor-based navigation
- Bounded history (50 operations past/future from cursor)
- Stateless rendering of operation pipeline
"""

from pathlib import Path
from typing import List
import numpy as np
import cv2
from operations import Operation


class PanelSession:
    """
    Manages a single manga panel and its operation timeline.

    The session maintains a cursor-based timeline where:
    - cursor points to the current position in the operations list (0..len(operations))
    - rendered image = original_image + operations[:cursor] applied sequentially
    - history is bounded to 50 ops past and 50 ops future from cursor
    """

    def __init__(self, image_dir: Path):
        """
        Initialize session with images from directory.

        Args:
            image_dir: Directory containing manga panel images (JP2, PNG, JPG)
        """
        # Load and sort image paths
        self.image_paths: List[Path] = []
        for ext in ['*.jp2', '*.JP2', '*.png', '*.PNG', '*.jpg', '*.JPG', '*.jpeg', '*.JPEG']:
            self.image_paths.extend(image_dir.glob(ext))
        self.image_paths = sorted(self.image_paths)

        if not self.image_paths:
            raise ValueError(f"No images found in {image_dir}")

        self.current_index: int = 0

        # Timeline state
        self.original_image: np.ndarray = None
        self.operations: List[Operation] = []
        self.cursor: int = 0

        # Load first image
        self._load_current_panel()

    def _load_current_panel(self):
        """Load image at current_index as grayscale."""
        path = self.image_paths[self.current_index]
        self.original_image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)

        if self.original_image is None:
            raise ValueError(f"Failed to load image: {path}")

    # Timeline Editing Methods

    def insert_operation(self, op: Operation):
        """
        Insert operation at cursor position.

        The operation is inserted at the cursor, cursor is incremented,
        and history is trimmed to maintain bounds.

        Args:
            op: Operation to insert
        """
        self.operations.insert(self.cursor, op)
        self.cursor += 1
        self._trim_history()

    def delete_operation(self):
        """
        Delete operation before cursor.

        If cursor > 0, deletes operations[cursor-1] and decrements cursor.
        """
        if self.cursor > 0:
            del self.operations[self.cursor - 1]
            self.cursor -= 1
            self._trim_history()

    def move_cursor_back(self):
        """Move cursor backward (undo)."""
        self.cursor = max(0, self.cursor - 1)

    def move_cursor_forward(self):
        """Move cursor forward (redo)."""
        self.cursor = min(len(self.operations), self.cursor + 1)

    def reset_operations(self):
        """Clear all operations and reset cursor to 0."""
        self.operations.clear()
        self.cursor = 0

    # Panel Navigation Methods

    def next_panel(self):
        """
        Move to next panel and reset operations.

        Increments current_index, reloads image, and clears timeline.
        """
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self._load_current_panel()
            self.reset_operations()

    def previous_panel(self):
        """
        Move to previous panel and reset operations.

        Decrements current_index, reloads image, and clears timeline.
        """
        if self.current_index > 0:
            self.current_index -= 1
            self._load_current_panel()
            self.reset_operations()

    # Bounded History Management

    def _trim_history(self):
        """
        Enforce bounded history: 50 ops past/future of cursor.

        Trims operations list to keep at most 100 operations total
        (50 before cursor + 50 after cursor).
        """
        # Trim past
        if self.cursor > 50:
            trim_count = self.cursor - 50
            self.operations = self.operations[trim_count:]
            self.cursor -= trim_count

        # Trim future
        if len(self.operations) - self.cursor > 50:
            self.operations = self.operations[:self.cursor + 50]

    # Rendering Methods

    def render(self) -> np.ndarray:
        """
        Stateless render: apply operations[:cursor] to original_image.

        Returns:
            Rendered image with operations applied
        """
        img = self.original_image.copy()
        for op in self.operations[:self.cursor]:
            img = op.apply(img)
        return img

    def render_at_cursor(self, target_cursor: int) -> np.ndarray:
        """
        Render image at specific cursor position.

        Used for comparison view to show different timeline states.

        Args:
            target_cursor: Cursor position to render at

        Returns:
            Rendered image at target cursor position
        """
        img = self.original_image.copy()
        for op in self.operations[:target_cursor]:
            img = op.apply(img)
        return img

    # Status Methods

    def get_current_filename(self) -> str:
        """Return current panel filename."""
        return self.image_paths[self.current_index].name

    def get_status(self) -> str:
        """
        Return status string: filename and cursor position.

        Returns:
            Status string formatted as "filename.jp2 | Cursor: 5/12"
        """
        return f"{self.get_current_filename()} | Cursor: {self.cursor}/{len(self.operations)}"

    def get_panel_info(self) -> str:
        """
        Return panel navigation info.

        Returns:
            Info string formatted as "Panel: 5/396"
        """
        return f"Panel: {self.current_index + 1}/{len(self.image_paths)}"
