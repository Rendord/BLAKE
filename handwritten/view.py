from PyQt6.QtWidgets import QApplication, QWidget, QSizePolicy, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
import cv2
from pathlib import Path
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

#APPLICATION RUN

panelPath = Path("manga_scans/jp2/BLAME!_Master_Edition_v01__0000.jp2")
img = cv2.imread(str(panelPath), cv2.IMREAD_GRAYSCALE)

app = QApplication([])

#TODO add TImeLineApplication class that inherits from QWidget
window = QWidget()
main_layout = QVBoxLayout(window)
timeline_context = QWidget()
timeline_context_layout = QHBoxLayout(timeline_context)
navigation = QWidget()
navigation_layout = QHBoxLayout(navigation)

page_count = ExpandingTextLabel("Panel: 0")
remove_op = ExpandingButton("-")
operation_dropdown = QComboBox()
operation_dropdown.addItems(["Threshold", "MorphOpen", "MorphClose"])
insert_op = ExpandingButton("+")
iteration = ExpandingTextLabel("Iteration: 0/0")
iteration.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

timeline_context_layout.addWidget(page_count, stretch=10)
timeline_context_layout.addWidget(remove_op, stretch=5)
timeline_context_layout.addWidget(operation_dropdown, stretch=70)
timeline_context_layout.addWidget(insert_op, stretch=5)
timeline_context_layout.addWidget(iteration, stretch=10, alignment=Qt.AlignmentFlag.AlignRight)



left_arrow = ExpandingButton("←")
right_arrow = ExpandingButton("→")
up_down = QWidget()
up_down_layout = QVBoxLayout(up_down)
up_arrow = ExpandingButton("↑")
down_arrow = ExpandingButton("↓")
up_down_layout.addWidget(up_arrow)
up_down_layout.addWidget(down_arrow)
up_down_layout.setSpacing(1)
up_down_layout.setContentsMargins(5, 2, 5, 2)

navigation_layout.addWidget(left_arrow, stretch=10)
navigation_layout.addWidget(up_down, stretch=80)
navigation_layout.addWidget(right_arrow, stretch=10)

label = QLabel()
red = ColorSquare('red')
red_2 = ColorSquare('red')


# red_3 = ColorSquare('red')
# blue = ColorSquare('blue')
# yellow = ColorSquare('yellow')

# 1) screen size
screen = app.primaryScreen()
avail = screen.availableGeometry()      # excludes taskbar/dock
sw, sh = avail.width(), avail.height()

HEIGHT = int(sh * 0.9)
WIDTH = int(HEIGHT * 0.7)

panel_w, panel_h = int(WIDTH * 0.85), int(HEIGHT * 0.85)


qimg = matLikeToQImage(img)
pixmap = QPixmap.fromImage(qimg)
scaled_pixmap = pixmap.scaled(
    panel_w,
    panel_h,
    Qt.AspectRatioMode.KeepAspectRatio,
    Qt.TransformationMode.SmoothTransformation
)
label.setPixmap(scaled_pixmap)

main_layout.addWidget(timeline_context, stretch=5)
main_layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
main_layout.addWidget(navigation, stretch=10)




window.resize(WIDTH,HEIGHT)
window.setFixedSize(window.size())
window.show()

app.exec()