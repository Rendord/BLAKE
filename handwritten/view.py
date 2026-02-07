from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage
import cv2
from cv2.typing import MatLike
import np

class ColorSquare(QWidget):
    def __init__(self, color: str):
        super().__init__()
        # Stretch to fill grid cell
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Set background color
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background-color: {color};")


app = QApplication([])



window = QWidget()

grid = QGridLayout(window)

red = ColorSquare('red')
red_2 = ColorSquare('red')
red_3 = ColorSquare('red')
blue = ColorSquare('blue')
yellow = ColorSquare('yellow')


grid.addWidget(yellow, 0, 0, 1, 1)
grid.addWidget(blue, 0, 2, 2, 1)

#grid.addWidget(red, 2, 1, 1, 3)

def returnQImage(img: MatLike) -> QImage:
    validateImg()
    if img.ndim == 2:
        rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    if img.shape[2] == 3:
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    if img.shape[2] == 4:
        rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

    if rgb:
        return QImage(rgb.data, rgb.shape[0], rgb.shape[1], rgb.strides[0], QImage.Format_RGB888).copy()
    else:
        #TODO implement placeholder image or similar
        return QImage()

def validateImg(img: MatLike):
    if img.dtype != np.uint8:
        raise TypeError("Expected uint8 image")
    if img.ndim not in (2, 3): 
        raise ValueError("Not an image") 
    if img.ndim == 3 and img.shape[2] not in (3, 4): 
        raise ValueError("Unsupported channel count")



window.resize(1200,800)
window.show()

app.exec()