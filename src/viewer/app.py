import viewer
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtCore import Qt, QThread
from viewer.view import TimeLineApplicationView
from viewer.opencv_controller import OpenCVController
from viewer.opencv_controller import RenderJob
from viewer.types import Settings
from dataclasses import asdict
from pathlib import Path
import json
import sys

def _write_state(page_number: int):
    #/*app: QApplication,**/
    #app.primaryScreen().availableGeometry().height()
    #app
    #"rel_width": relative_width, "rel_height": relative_height, 

    settings = asdict(Settings(index=page_number))
    settings_path = Path("session/session.json")

    settings_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file=settings_path, mode="w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)


def _load_state() -> Settings:
    settings_path = Path("session/session.json")

    if settings_path.exists():
        with open(file=settings_path, mode="r", encoding="utf-8") as f:
            settings = json.load(f)
            return Settings(**settings)
    else:
        return Settings(index=0)


def main():
    app = QApplication([])

    settings = _load_state()

    # get screen size for scaling
    window_height = app.primaryScreen().availableGeometry().height()      # excludes taskbar/dock
    dpr = app.primaryScreen().devicePixelRatio()

    #TODO make resolution checking and window sizing more robust
    HEIGHT = int(window_height * 0.9)
    WIDTH = int(HEIGHT * 0.7)

    scaled_resolution = int(WIDTH * 0.85), int(HEIGHT * 0.85) #tuple

    #TODO NEEDS TO HANDLE EMPTY IMAGE FOLDER
    
    controller = OpenCVController(settings.index, scaled_resolution, dpr)
    #TODO decouple image loading and panel session (Create a worker vs panelsession)
    #initialize viewing session

    #TODO add constants module
    page_count = controller.loadImagePaths('manga_scans/jp2')

    #initialize application window
    window = TimeLineApplicationView(page_count=page_count, index=settings.index, scaled_resolution=scaled_resolution)

    window.request_page.connect(controller.fetchPage)
    window.insert_op.connect(controller.insertOperation)
    window.remove_op.connect(controller.removeOperation)
    window.ascend_timeline.connect(controller.onAscend)
    window.descend_timeline.connect(controller.onDescend)
    controller.send_image.connect(window.displayPixmap)
    controller.timeline_size_change.connect(window.changeTimeLineSize)

    # Create a shortcut for the "Insert" action
    QShortcut(QKeySequence("+"), window, activated=window.onInsert)
    QShortcut(QKeySequence("="), window, activated=window.onInsert)
    QShortcut(QKeySequence("-"), window, activated=window.onRemove)
    QShortcut(QKeySequence(Qt.Key.Key_Left), window, activated=window.onPrevious)
    QShortcut(QKeySequence(Qt.Key.Key_Right), window, activated=window.onNext)
    QShortcut(QKeySequence(Qt.Key.Key_Up), window, activated=window.onAscend)
    QShortcut(QKeySequence(Qt.Key.Key_Down), window, activated=window.onDescend)

    #TODO try out glymur to see if performance is noticesably slower (it should be)
    controller.queueRender(RenderJob(settings.index, scaled_resolution, dpr, 0)) #, path=controller.image_paths[0]
    controller.prefetchRenders()

    def close_app():
        controller.stop()
        for thread, _ in controller.workers:
            thread.quit()
        for thread, _ in controller.workers:
            thread.wait()
        _write_state(window.index)
        
        sys.exit()

    window.resize(WIDTH,HEIGHT)
    window.setFixedSize(window.size())

    app.aboutToQuit.connect(close_app)

    window.show()
    
    QShortcut(QKeySequence("Escape"), window, activated=window.close)
    
    app.exec()


if __name__ == '__main__':
    main()