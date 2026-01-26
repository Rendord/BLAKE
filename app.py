"""
Interactive Manga Panel Operation Timeline Tool

Main GUI application using PyQt6 for:
- Image display and preview
- Operation selection and parameter editing
- Timeline navigation with keyboard controls
- Side-by-side comparison view
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QSpinBox, QDoubleSpinBox, QStatusBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap, QKeyEvent
import cv2
import numpy as np

from session import PanelSession
from operations import create_operation


class MangaOperationsApp(QMainWindow):
    """
    Main application window for interactive manga panel operations.

    Provides GUI for selecting operations, adjusting parameters, and
    navigating through a timeline of applied operations.
    """

    def __init__(self, image_dir: Path):
        """
        Initialize the application.

        Args:
            image_dir: Directory containing manga panel images
        """
        super().__init__()

        # Initialize session
        self.session = PanelSession(image_dir)

        # Storage for current parameter widgets
        self.param_widgets = {}

        # Setup UI
        self.init_ui()

        # Initial display
        self.refresh_display()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Interactive Manga Operations")
        self.setGeometry(100, 100, 1200, 900)

        # Central widget and layout
        central = QWidget()
        main_layout = QVBoxLayout(central)

        # Image display area (takes most space)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setScaledContents(False)
        self.image_label.setMinimumSize(800, 600)
        main_layout.addWidget(self.image_label, stretch=10)

        # Controls panel
        controls = QWidget()
        controls_layout = QHBoxLayout(controls)

        # Operation dropdown
        controls_layout.addWidget(QLabel("Operation:"))
        self.op_dropdown = QComboBox()
        self.op_dropdown.addItems(['Threshold', 'Rotate', 'MorphOpen', 'MorphClose', 'Invert'])
        self.op_dropdown.currentTextChanged.connect(self.on_operation_changed)
        controls_layout.addWidget(self.op_dropdown)

        # Parameter inputs container (dynamic)
        self.param_container = QWidget()
        self.param_layout = QHBoxLayout(self.param_container)
        controls_layout.addWidget(self.param_container)

        # Apply button (visual only - '+' key does the action)
        apply_btn = QPushButton("Apply (+)")
        apply_btn.clicked.connect(self.apply_operation)
        controls_layout.addWidget(apply_btn)

        # Delete button (visual only - '-' key does the action)
        delete_btn = QPushButton("Delete (-)")
        delete_btn.clicked.connect(self.delete_operation)
        controls_layout.addWidget(delete_btn)

        main_layout.addWidget(controls, stretch=1)

        # Help text
        help_text = QLabel(
            "Keys: [+] Apply | [-] Delete | [↑/↓] Undo/Redo | "
            "[←/→] Prev/Next Panel | [R] Reset | [C] Compare"
        )
        help_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        help_text.setStyleSheet("color: gray; font-size: 10pt;")
        main_layout.addWidget(help_text)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.setCentralWidget(central)

        # Initialize parameter widgets for default operation
        self.on_operation_changed(self.op_dropdown.currentText())

    def on_operation_changed(self, op_type: str):
        """
        Rebuild parameter inputs based on selected operation.

        Args:
            op_type: Selected operation type name
        """
        # Clear existing parameter widgets
        while self.param_layout.count():
            child = self.param_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.param_widgets = {}

        # Add new parameter widgets based on operation type
        if op_type == 'Threshold':
            self.param_layout.addWidget(QLabel("Value (0=OTSU):"))
            threshold_spin = QSpinBox()
            threshold_spin.setRange(0, 255)
            threshold_spin.setValue(128)
            self.param_layout.addWidget(threshold_spin)
            self.param_widgets = {'threshold_value': threshold_spin}

        elif op_type == 'Rotate':
            self.param_layout.addWidget(QLabel("Angle:"))
            angle_spin = QDoubleSpinBox()
            angle_spin.setRange(-180, 180)
            angle_spin.setSingleStep(1.0)
            angle_spin.setValue(0.0)
            angle_spin.setDecimals(1)
            self.param_layout.addWidget(angle_spin)

            # Quick rotate buttons
            for angle in [-90, -1, 1, 90]:
                btn = QPushButton(f"{angle:+}°")
                btn.clicked.connect(lambda checked, a=angle, spin=angle_spin: spin.setValue(a))
                self.param_layout.addWidget(btn)

            self.param_widgets = {'angle_deg': angle_spin}

        elif op_type in ['MorphOpen', 'MorphClose']:
            self.param_layout.addWidget(QLabel("Kernel Size:"))
            kernel_spin = QSpinBox()
            kernel_spin.setRange(3, 15)
            kernel_spin.setSingleStep(2)  # Keep odd
            kernel_spin.setValue(3)
            self.param_layout.addWidget(kernel_spin)
            self.param_widgets = {'kernel_size': kernel_spin}

        elif op_type == 'Invert':
            self.param_layout.addWidget(QLabel("(no parameters)"))
            self.param_widgets = {}

    def apply_operation(self):
        """Apply currently selected operation with current parameters."""
        op_type = self.op_dropdown.currentText()

        # Get parameter values from widgets
        params = {}
        for param_name, widget in self.param_widgets.items():
            if isinstance(widget, QSpinBox):
                params[param_name] = widget.value()
            elif isinstance(widget, QDoubleSpinBox):
                params[param_name] = widget.value()

        # Create and insert operation
        try:
            op = create_operation(op_type, **params)
            self.session.insert_operation(op)
            self.refresh_display()
        except Exception as e:
            self.status_bar.showMessage(f"Error applying operation: {e}", 3000)

    def delete_operation(self):
        """Delete operation at cursor."""
        self.session.delete_operation()
        self.refresh_display()

    def refresh_display(self):
        """Update image display and status bar."""
        # Render current state
        img = self.session.render()

        # Convert NumPy array to QPixmap
        q_img = self.numpy_to_qimage(img)
        pixmap = QPixmap.fromImage(q_img)

        # Scale to fit label while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)

        # Update status bar
        status_text = f"{self.session.get_status()} | {self.session.get_panel_info()}"
        self.status_bar.showMessage(status_text)

    def numpy_to_qimage(self, img: np.ndarray) -> QImage:
        """
        Convert NumPy array to QImage.

        Args:
            img: NumPy array (grayscale or BGR color)

        Returns:
            QImage for display
        """
        height, width = img.shape[:2]

        if len(img.shape) == 2:  # Grayscale
            bytes_per_line = width
            return QImage(img.data, width, height, bytes_per_line, QImage.Format.Format_Grayscale8)
        else:  # Color (BGR -> RGB)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            bytes_per_line = 3 * width
            return QImage(img_rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

    def show_comparison(self):
        """
        Display side-by-side comparison of last 4 timeline states.

        Opens a modal OpenCV window showing timeline progression.
        """
        cursor = self.session.cursor

        # Calculate 4 cursor positions ending at current cursor
        # Example: cursor=5 -> positions=[2, 3, 4, 5]
        positions = [cursor - 3 + i for i in range(4)]
        positions = [max(0, p) for p in positions if p <= cursor]

        # Ensure we have at least the current position
        if cursor not in positions:
            positions.append(cursor)

        # Limit to 4 positions
        positions = positions[-4:]

        if not positions:
            self.status_bar.showMessage("No operations to compare", 2000)
            return

        # Render each state
        images = []
        for pos in positions:
            img = self.session.render_at_cursor(pos)

            # Resize for display (max height 800px to fit screen)
            h, w = img.shape[:2]
            if h > 800:
                scale = 800 / h
                new_h, new_w = int(h * scale), int(w * scale)
                img = cv2.resize(img, (new_w, new_h))

            # Add text label showing cursor position
            img_labeled = img.copy()
            cv2.putText(
                img_labeled,
                f"Cursor: {pos}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (255, 255, 255) if img_labeled.dtype == np.uint8 else (1.0, 1.0, 1.0),
                2
            )
            images.append(img_labeled)

        # Ensure all images have same height for concatenation
        if images:
            max_height = max(img.shape[0] for img in images)
            images_padded = []
            for img in images:
                if img.shape[0] < max_height:
                    padding = max_height - img.shape[0]
                    img = cv2.copyMakeBorder(
                        img, 0, padding, 0, 0,
                        cv2.BORDER_CONSTANT, value=0
                    )
                images_padded.append(img)

            # Concatenate horizontally
            comparison_strip = cv2.hconcat(images_padded)

            # Display modal window
            cv2.imshow("Timeline Comparison (press any key to close)", comparison_strip)
            cv2.waitKey(0)
            cv2.destroyWindow("Timeline Comparison (press any key to close)")

    def keyPressEvent(self, event: QKeyEvent):
        """
        Handle keyboard shortcuts.

        Args:
            event: Key event
        """
        key = event.key()

        if key == Qt.Key.Key_Plus or key == Qt.Key.Key_Equal:
            # '+': Apply current operation
            self.apply_operation()

        elif key == Qt.Key.Key_Minus or key == Qt.Key.Key_Underscore:
            # '-': Delete operation at cursor
            self.delete_operation()

        elif key == Qt.Key.Key_Up:
            # Up: Move cursor back (undo)
            self.session.move_cursor_back()
            self.refresh_display()

        elif key == Qt.Key.Key_Down:
            # Down: Move cursor forward (redo)
            self.session.move_cursor_forward()
            self.refresh_display()

        elif key == Qt.Key.Key_Left:
            # Left: Previous panel
            self.session.previous_panel()
            self.refresh_display()

        elif key == Qt.Key.Key_Right:
            # Right: Next panel
            self.session.next_panel()
            self.refresh_display()

        elif key == Qt.Key.Key_R:
            # 'r': Reset operations
            self.session.reset_operations()
            self.refresh_display()

        elif key == Qt.Key.Key_C:
            # 'c': Open comparison view
            self.show_comparison()

        else:
            super().keyPressEvent(event)


def main():
    """Main entry point for the application."""
    # Default to manga_scans/jp2 directory
    default_dir = Path(__file__).parent / "manga_scans" / "jp2"

    # Allow command line argument to override
    if len(sys.argv) > 1:
        image_dir = Path(sys.argv[1])
    else:
        image_dir = default_dir

    if not image_dir.exists():
        print(f"Error: Image directory not found: {image_dir}")
        print(f"Usage: python {sys.argv[0]} [image_directory]")
        sys.exit(1)

    # Create and run application
    app = QApplication(sys.argv)
    window = MangaOperationsApp(image_dir)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
