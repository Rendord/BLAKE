from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtCore import Qt, QThread
from handwritten.view import TimeLineApplicationView
from handwritten.opencv_controller import OpenCVController
import sys

def main():
    app = QApplication([])

    # get screen size for scaling
    window_height = app.primaryScreen().availableGeometry().height()      # excludes taskbar/dock

    #TODO make resolution checking and window sizing more robust
    HEIGHT = int(window_height * 0.9)
    WIDTH = int(HEIGHT * 0.7)

    scaled_resolution = int(WIDTH * 0.85), int(HEIGHT * 0.85) #tuple

    controller_thread = QThread()
    controller = OpenCVController()
    controller.moveToThread(controller_thread)
    controller_thread.start()
    #TODO decouple image loading and panel session (Create a worker vs panelsession)
    #initialize viewing session

    page_count = controller.loadImagePaths('manga_scans/jp2')

    pixmap = controller.returnPixMapAtIndex(0, scaled_resolution)

    #initialize application window
    window = TimeLineApplicationView(page_count=page_count, pixmap=pixmap, scaled_resolution=scaled_resolution)

    window.request_page.connect(controller.returnPixMapAtIndex)
    controller.pixmap_ready.connect(window.displayPixmap)

    window.resize(WIDTH,HEIGHT)
    window.setFixedSize(window.size())
    window.show()
    QShortcut(QKeySequence("Escape"), window, activated=window.close)
    QShortcut(QKeySequence(Qt.Key.Key_Right), window, activated=window.navigation_controls.next)
    QShortcut(QKeySequence(Qt.Key.Key_Left), window, activated=window.navigation_controls.previous)

    controller_thread.quit()      # ask event loop to stop
    controller_thread.wait()      # block until it finishes

    sys.exit(app.exec())

if __name__ == '__main__':
    main()