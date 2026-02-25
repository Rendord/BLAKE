from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QShortcut, QKeySequence
from handwritten.view import TimeLineApplicationView, matLikeToQImage
from handwritten.panelsession import PanelSession
import cv2
import sys
from pathlib import Path

def main():
    app = QApplication([])

    # get screen size for scaling
    screen = app.primaryScreen()
    avail = screen.availableGeometry()      # excludes taskbar/dock
    sw, sh = avail.width(), avail.height()

    HEIGHT = int(sh * 0.9)
    WIDTH = int(HEIGHT * 0.7)

    panel_w, panel_h = int(WIDTH * 0.85), int(HEIGHT * 0.85)


    #initialize viewing session
    panel_session = PanelSession()
    page_count = panel_session.load_image_paths('manga_scans\jp2')

    #load manga panel
    panelPath = panel_session.image_paths[0]
    img = cv2.imread(str(panelPath), cv2.IMREAD_GRAYSCALE)
    qimg = matLikeToQImage(img)
    pixmap = QPixmap.fromImage(qimg)
    scaled_pixmap = pixmap.scaled(
        panel_w,
        panel_h,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation
    )

    #initialize application window
    window = TimeLineApplicationView(scaled_pixmap)
    window.resize(WIDTH,HEIGHT)
    window.setFixedSize(window.size())
    window.show()
    QShortcut(QKeySequence("Escape"), window, activated=window.close)

    sys.exit(app.exec())

if __name__ == '__main__':
    main()