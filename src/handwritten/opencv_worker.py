from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .opencv_controller import OpenCVController
from .types import RenderJob
from PyQt6.QtCore import pyqtSignal, QObject, Qt
from PyQt6.QtGui import QImage
import cv2
import numpy as np
import time
import pyvips
from pathlib import Path
from cv2.typing import MatLike


class OpenCVWorker(QObject):
    controller: OpenCVController
    running: bool
    finished = pyqtSignal()
    rendered = pyqtSignal(RenderJob, QImage)

    def __init__(self, controller: OpenCVController):
        super().__init__()
        self.controller = controller
        self.running = True
    
    def run(self):   # this is the worker loop
        while self.running:
            _, _, job = self.controller.priority_queue.get()

            if job is None:
                self.running = False
                self.finished.emit()
                return
            
            if abs(self.controller.current_index - job.index) > 8:
                continue

            result = self.renderQImage(job)

            self.rendered.emit(job, result)

    def renderQImage(self, render_job: RenderJob) -> QImage:
        #print(render_job.index)

        dpr = self.controller.device_pixel_ratio
        
        # 2. Calculate PHYSICAL pixels
        phys_w, phys_h = int(render_job.resolution[0] * dpr), int(render_job.resolution[1] * dpr)

        path = self.controller.image_paths[render_job.index]
        start_time = time.perf_counter()
        try:
            img = self.read_jp2(path, phys_w, phys_h)
        except Exception as e:
            print("read exception" + str(e))
            img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        elapsed = time.perf_counter() - start_time
        print(f"DEBUG: Loaded in {elapsed:.4f}s")
        image = (
            matLikeToQImage(img)
        )
        image.setDevicePixelRatio(dpr)
    
        return image
    
    def read_jp2(self, path: str, target_width: int, target_height: int) -> MatLike:

        absolute_path = str(Path(path).resolve())

        #thumbnail for wicked fast loading
        vips_img = pyvips.Image.thumbnail(absolute_path, target_width, height=target_height, size="force")

        #vips_img = pyvips.Image.new_from_file(absolute_path, access="sequential", shrink=2)
        # Convert to NumPy (This is where the actual parallel decoding happens)
        img_np = np.ndarray(
        buffer=vips_img.write_to_memory(),
        dtype=np.uint8,
        shape=[vips_img.height, vips_img.width, vips_img.bands]
        )
        
        validateImg(img_np)

        return img_np
        

def validateImg(img: MatLike):
    if img.dtype != np.uint8:
        raise TypeError("Expected uint8 image")
    if img.ndim not in (2, 3): 
        raise ValueError("Not an image") 
    if img.ndim == 3 and img.shape[2] not in (3, 4): 
        raise ValueError("Unsupported channel count")        

def matLikeToQImage(img: np.ndarray) -> QImage:
    h, w = img.shape[:2]
    # If 2D array, it's grayscale. If 3D, check the last dimension RGB vs RGBA
    bands = img.shape[2] if img.ndim == 3 else 1
    
    if bands == 1:
        fmt = QImage.Format.Format_Grayscale8
    elif bands == 3:
        fmt = QImage.Format.Format_RGB888
    elif bands == 4:
        fmt = QImage.Format.Format_RGBA8888
    else:
        raise ValueError(f"Unsupported bands: {bands}")

    return QImage(img.data, w, h, img.strides[0], fmt).copy()


def handleChannelOrder(img: MatLike) -> MatLike:
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
    
    return rgb

def print_debug(render_job, image, dpr, phys_w, phys_h):
    # --- WORKER DEBUG ---
    print(f"\n[Worker: {render_job.index}]")
    print(f"  - Requested Logical: {render_job.resolution[0]}x{render_job.resolution[1]}")
    print(f"  - Target Physical (DPR {dpr}): {phys_w}x{phys_h}")
    print(f"  - Actual Buffer Size: {image.width()}x{image.height()}")
    print(f"  - QImage Object DPR: {image.devicePixelRatio()}")
