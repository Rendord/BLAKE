from PyQt6.QtWidgets import QWidget, QSizePolicy, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
import cv2
from cv2.typing import MatLike
import numpy as np

class ColorSquare(QWidget):
    def __init__(self, color: str):
        super().__init__()
        # Stretch to fill grid cell
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Set background color
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background-color: {color};")

class ExpandingButton(QPushButton):
    def __init__(self, text: str):
        super().__init__(text)
        # Stretch to fill grid cell
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

class ExpandingTextLabel(QLabel):
    def __init__(self, text: str):
        super().__init__(text)
        # Stretch to fill grid cell
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

class TimeLineContext(QWidget):
    layout: QHBoxLayout
    page_count: ExpandingTextLabel
    remove_op: ExpandingButton
    op_dropdown: QComboBox
    insert_op: ExpandingButton
    iteration_idx: ExpandingTextLabel

    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.page_count = ExpandingTextLabel("Panel: 0")
        self.remove_op = ExpandingButton("-")
        self.op_dropdown = QComboBox()
        self.op_dropdown.addItems(["Threshold", "MorphOpen", "MorphClose"])
        self.insert_op = ExpandingButton("+")
        self.iteration_idx = ExpandingTextLabel("Iteration: 0/0")
        self.iteration_idx.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.layout.addWidget(self.page_count, stretch=10)
        self.layout.addWidget(self.remove_op, stretch=5)
        self.layout.addWidget(self.op_dropdown, stretch=70)
        self.layout.addWidget(self.insert_op, stretch=5)
        self.layout.addWidget(self.iteration_idx, stretch=10, alignment=Qt.AlignmentFlag.AlignRight)

class NavigationControls(QWidget):
    layout: QHBoxLayout
    left_arrow: ExpandingButton
    right_arrow: ExpandingButton
    up_arrow: ExpandingButton
    down_arrow: ExpandingButton

    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)
        #create arrow keys
        self.left_arrow = ExpandingButton("←")
        self.right_arrow = ExpandingButton("→")
        self.up_arrow = ExpandingButton("↑")
        self.down_arrow = ExpandingButton("↓")

        #create middle layout
        up_down = QVBoxLayout()
        up_down.addWidget(self.up_arrow)
        up_down.addWidget(self.down_arrow)
        up_down.setSpacing(1)
        up_down.setContentsMargins(5, 2, 5, 2)

        self.layout.addWidget(self.left_arrow, stretch=10)
        self.layout.addLayout(up_down, stretch=80)
        self.layout.addWidget(self.right_arrow, stretch=10)

class TimeLineApplicationView(QWidget):
    layout: QVBoxLayout
    timeline_context: TimeLineContext
    panel_frame: QLabel
    navigation_controls: NavigationControls

    def __init__(self, pixmap: QPixmap):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.timeline_context = TimeLineContext()
        self.panel_frame = QLabel()
        self.navigation_controls = NavigationControls()
        self.panel_frame.setPixmap(pixmap)
        self.layout.addWidget(self.timeline_context, stretch=5)
        self.layout.addWidget(self.panel_frame, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.navigation_controls, stretch=10)


def validateImg(img: MatLike):
    if img.dtype != np.uint8:
        raise TypeError("Expected uint8 image")
    if img.ndim not in (2, 3): 
        raise ValueError("Not an image") 
    if img.ndim == 3 and img.shape[2] not in (3, 4): 
        raise ValueError("Unsupported channel count")        

#TODO Write QTMatLikeWrapper class that infers the type when constructed and has a to QTImage function
def matLikeToQImage(img: MatLike) -> QImage:
    validateImg(img)

    # Grayscale
    if img.ndim == 2:
        rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

    # Color
    elif img.ndim == 3:
        if img.shape[2] == 3:
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        elif img.shape[2] == 4:
            rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
        else:
            raise ValueError("Unsupported channel count")

    else:
        raise ValueError("Unsupported image dimensionality")
    
    h, w, _ = rgb.shape
    return QImage(
        rgb.data,
        w,               # width
        h,               # height
        rgb.strides[0],
        QImage.Format.Format_RGB888
    ).copy()
