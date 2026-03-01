import handwritten
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtCore import Qt, QThread
from handwritten.view import TimeLineApplicationView
from handwritten.opencv_controller import OpenCVController
from handwritten.opencv_controller import RenderJob
import sys

def main():
    app = QApplication([])

    # get screen size for scaling
    window_height = app.primaryScreen().availableGeometry().height()      # excludes taskbar/dock
    dpr = app.primaryScreen().devicePixelRatio()

    #TODO make resolution checking and window sizing more robust
    HEIGHT = int(window_height * 0.9)
    WIDTH = int(HEIGHT * 0.7)

    scaled_resolution = int(WIDTH * 0.85), int(HEIGHT * 0.85) #tuple

    
    
    controller = OpenCVController(scaled_resolution, dpr)
    #TODO decouple image loading and panel session (Create a worker vs panelsession)
    #initialize viewing session

    #TODO refactor setup so first page to display is rendered dynamically
    page_count = controller.loadImagePaths('manga_scans/jp2')

    #initialize application window
    window = TimeLineApplicationView(page_count=page_count, scaled_resolution=scaled_resolution)

    window.request_page.connect(controller.fetchPage)
    controller.send_image.connect(window.displayPixmap)

    #TODO refactor setup so first page to display is rendered dynamically
    controller.queueRender(RenderJob(0, scaled_resolution, 0)) #, path=controller.image_paths[0]
    controller.prefetchRenders()

    def close_app():
        controller.stop()
        for thread, _ in controller.workers:
            thread.quit()
        for thread, _ in controller.workers:
            thread.wait()
        
        sys.exit()

    window.resize(WIDTH,HEIGHT)
    window.setFixedSize(window.size())

    app.aboutToQuit.connect(close_app)

    window.show()
    
    QShortcut(QKeySequence("Escape"), window, activated=window.close)
    
    app.exec()


if __name__ == '__main__':
    main()