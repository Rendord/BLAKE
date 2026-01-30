from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QSizePolicy


class ColorSquare(QWidget):
    def __init__(self, color: str):
        super().__init__()
        # Stretch to fill grid cell
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Set background color
        self.setStyleSheet(f"background-color: {color};")


app = QApplication([])



window = QWidget()

grid = QGridLayout(window)

red = ColorSquare('red')
blue = ColorSquare('blue')
yellow = ColorSquare('yellow')


grid.addWidget(red, 1, 1)
grid.addWidget(red, 0, 1)
grid.addWidget(red, 1, 1)



window.resize(1200,800)
window.show()

app.exec()