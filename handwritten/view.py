from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QSizePolicy
from PyQt6.QtCore import Qt


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




window.resize(1200,800)
window.show()

app.exec()