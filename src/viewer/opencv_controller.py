from viewer.panelsession import OperationTimeline
from viewer.cache import LRUCache
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtGui import QImage
from PyQt6.QtCore import QThread
from viewer.types import RenderJob
from viewer.operations import VisOp
from typing import List, Tuple
from pathlib import Path
from queue import PriorityQueue
from itertools import count
from viewer.opencv_worker import OpenCVWorker

class OpenCVController(QObject):
    timeline: OperationTimeline
    timeline_size_change = pyqtSignal(int)
    send_image = pyqtSignal(QImage)
    image_paths: List[Path]
    current_index: int
    target_resolution: Tuple[int, int]
    priority_queue: PriorityQueue[RenderJob]
    lru_cache: LRUCache[int, QImage]
    queued_indices: set
    device_pixel_ratio: float
    queue_seq: count
    workers: List[Tuple[QThread, OpenCVWorker]]


    def __init__(self, target_resolution: Tuple[int, int], dpr: float):
        super().__init__()
        self.timeline = OperationTimeline()
        self.priority_queue = PriorityQueue()
        self.queued_indices = set()
        self.image_paths = []
        self.queue_seq = count()
        self.workers = []
        self.current_index = 0 #I might want to extract some of this to an initialization step
        self.target_resolution = target_resolution
        self.device_pixel_ratio = dpr
        self.lru_cache = LRUCache(maxsize=25)
        self.workers.append((QThread(self),OpenCVWorker(self)))
        self.workers.append((QThread(self),OpenCVWorker(self)))
        for thread, worker in self.workers:
            worker.moveToThread(thread)
            thread.started.connect(worker.run)
            worker.finished.connect(thread.quit)
            worker.finished.connect(worker.deleteLater)
            thread.finished.connect(thread.deleteLater)
            worker.rendered.connect(self.handleRender)
            thread.start()
            
    def handleRender(self, render_job: RenderJob, image: QImage):
        if render_job.priority == 0:
            self.send_image.emit(image)

    def loadImagePaths(self, src: str | Path) -> int:
        src = Path(src)

        if not src.is_dir(): 
            return 0

        #TODO add constants module
        valid_extensions = {'.jp2','.png','.jpeg','.jpg','.webp'}

        self.image_paths.clear()
        for path in src.iterdir():
            if path.is_file() and path.suffix.lower() in valid_extensions:
                self.image_paths.append(path)

        self.image_paths.sort()

        return len(self.image_paths)
    
    def fetchPage(self, index: int):
        self.current_index = index
        self.prefetchRenders()
    
        render_job = RenderJob(index, self.target_resolution, self.device_pixel_ratio, 0) #  , self.image_paths[index]
        self.queueRender(render_job)

    def insertOperation(self, operation_name: str):
        vis_op = VisOp.create(operation_name)
        self.timeline.insertNode(vis_op)
        self.timeline_size_change.emit(self.timeline.timeline_size)
        self.timeline.ascend()
        self.queueRender(RenderJob(self.current_index, self.target_resolution, self.device_pixel_ratio, 0))

    def removeOperation(self):
        if self.timeline.timeline_size > 0:
            print("removed node: new timeline size " + str(self.timeline.timeline_size - 1))
        self.timeline.removeCurrent()
        self.timeline_size_change.emit(self.timeline.timeline_size)
        self.queueRender(RenderJob(self.current_index, self.target_resolution, self.device_pixel_ratio, 0))

    def onAscend(self):
        self.timeline.ascend()
        self.queueRender(RenderJob(self.current_index, self.target_resolution, self.device_pixel_ratio, 0))

    def onDescend(self):
        self.timeline.descend()
        self.queueRender(RenderJob(self.current_index, self.target_resolution, self.device_pixel_ratio, 0))
        
        
    def prefetchRenders(self):
        candidates: list[int] = []
        max_idx = len(self.image_paths) - 1
        c = self.current_index
        #sliding window dataclass? Or better approach 
        #amount of indices to prefetch around current index #TODO make sliding window configurable and add failsafe for sliding window that is too large, write function
        future = 4
        past = 4

        #sliding window that expands inwards near the edges
        if c - past < 0:
            future += abs(c - past)
            past -= abs(c - past)
        elif c + future > max_idx:
            past += (c + future) - max_idx  
            future -= (c + future) - max_idx

        # base window: -2..+2 excluding current
        for i in range(c - past, c + future + 1):
            if i == self.current_index:
                continue
            candidates.append(i)

        # de-dupe while preserving order
        seen = set()
        ordered = []
        for i in candidates:
            if i in seen:
                continue
            seen.add(i)
            ordered.append(i)

        # filter out cached + already queued
        for i in ordered:
            if i in self.lru_cache:
                continue
            if i in self.queued_indices:
                continue
            self.queueRender(RenderJob(i, self.target_resolution, self.device_pixel_ratio, 1)) #, self.image_paths[i]

    def queueRender(self, render_job: RenderJob):
        #packing queue item tuple with sequence and prio to determine priority
        prio = render_job.priority
        seq = next(self.queue_seq)
        job = render_job
        queue_item = (prio, seq, job)
        self.priority_queue.put(queue_item)
        #print("job queued")

    def stop(self):
        # one sentinel per worker
        for _ in self.workers:
            self.priority_queue.put((-1, next(self.queue_seq), None))