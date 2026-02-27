from .panelsession import OperationTimeline
from PyQt6.QtCore import pyqtSignal, QObject, Qt
from PyQt6.QtGui import QImage, QPixmap
import cv2
from cv2.typing import MatLike
from typing import List, Tuple
from functools import lru_cache
import numpy as np
from queue import Queue
from pathlib import Path

class OpenCVController(QObject):
    timeline: OperationTimeline
    pixmap_ready = pyqtSignal(QPixmap)
    image_paths: List[Path]
    current_index: int
    high_priority_q: Queue
    low_priority_q: Queue
    

    def __init__(self):
        super().__init__()
        self.timeline = OperationTimeline()
        self.high_priority_q = Queue()
        self.low_priority_q = Queue()
        self.image_paths = []

    def loadImagePaths(self, src: str | Path) -> int:
        src = Path(src)

        if not src.is_dir(): return 0

        valid_extensions = {'.jp2','.png','.jpeg','.jpg','.webp'}

        self.image_paths.clear()
        for path in src.iterdir():
            if path.is_file() and path.suffix.lower() in valid_extensions:
                self.image_paths.append(path)

        self.image_paths.sort()

        return len(self.image_paths)
    
    @lru_cache(maxsize=20)
    def renderPixmap(index, path: str, resolution: Tuple[int,int]):
        
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

        pixmap = QPixmap.fromImage(matLikeToQImage(img)).scaled(
            resolution[0], #width
            resolution[1], #height
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
    
        return pixmap

    #TODO add error handling and implement QSlot
    def returnPixMapAtIndex(self, index, resolution: Tuple[int,int]) -> QPixmap:
        
        path = self.image_paths[index]

        pixmap = self.renderPixmap(str(path), resolution)

        self.pixmap_ready.emit(pixmap)

        return pixmap



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


