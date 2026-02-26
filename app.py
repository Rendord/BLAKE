from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QShortcut, QKeySequence
from handwritten.view import TimeLineApplicationView
from handwritten.panelsession import PanelSession
import sys

def main():
    app = QApplication([])

    # get screen size for scaling
    window_height = app.primaryScreen().availableGeometry().height()      # excludes taskbar/dock

    #TODO make resolution checking and window sizing more robust
    HEIGHT = int(window_height * 0.9)
    WIDTH = int(HEIGHT * 0.7)

    scaled_resolution = int(WIDTH * 0.85), int(HEIGHT * 0.85) #tuple


    #TODO decouple image loading and panel session (Create a worker vs panelsession)
    #initialize viewing session
    panel_session = PanelSession()
    page_count = panel_session.loadImagePaths('manga_scans/jp2')
    pixmap = panel_session.returnPixMapAtIndex(0)


    #initialize application window
    window = TimeLineApplicationView(page_count=page_count, pixmap=pixmap, scaled_resolution=scaled_resolution)

    window.request_page.connect(panel_session.returnPixMapAtIndex)
    panel_session.pixmap_ready.connect(window.displayPixmap)

    window.resize(WIDTH,HEIGHT)
    window.setFixedSize(window.size())
    window.show()
    QShortcut(QKeySequence("Escape"), window, activated=window.close)

    sys.exit(app.exec())

if __name__ == '__main__':
    main()