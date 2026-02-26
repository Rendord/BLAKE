from typing import Protocol, Optional, List
from cv2.typing import MatLike
from dataclasses import dataclass
from pathlib import Path
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtGui import QImage, QPixmap
import cv2
from cv2.typing import MatLike
import numpy as np
import gc

class VisOp(Protocol):
    def apply(self) -> None: ...
    computed_image: MatLike #_typing.Union[cv2.mat_wrapper.Mat, NumPyArrayNumeric]
    next: Optional["VisOp"]
    previous: Optional["VisOp"]

class PanelSession(QObject):
    current: Optional[VisOp]
    tail: Optional[VisOp]
    timeline_size: int
    image_paths: List[Path]
    MAX_OPERATIONS: int = 50
    pixmap_ready = pyqtSignal(QPixmap)

    def __init__(self):
        super().__init__()
        self.current = None
        self.tail = None
        self.timeline_size = 0
        self.image_paths = []

    def insertOp(self, insertion:VisOp) -> None:
        #insert operation into timeline
        cur = self.current
        if cur.next is not None:
            cur.next.previous = insertion
        insertion.next = cur.next
        cur.next = insertion
        insertion.previous = cur

        if self.timeline_size >= self.MAX_OPERATIONS:
            #pop oldest
            old_tail = self.tail
            self.tail = old_tail.next
            self.tail.previous = None
            del old_tail
            gc.collect()
        else:
            self.timeline_size += 1

    def ascend(self) -> None:        
        cur = self.current
        if cur.next is not None:
            self.current = cur.next
        #else: pass
    
    def descend(self) -> None:        
        cur = self.current
        if cur.previous is not None:
            self.current = cur.previous
        #else: pass

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
    
    #TODO add error handling and caching
    def returnPixMapAtIndex(self, index: int) -> QPixmap:
    
        path = self.image_paths[index]

        img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        pixmap = QPixmap.fromImage(matLikeToQImage(img))

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
