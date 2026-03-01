from PyQt6.QtWidgets import QWidget, QSizePolicy, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox
from PyQt6.QtCore import QCoreApplication, QEventLoop, Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage
from handwritten import operations
from typing import Tuple

class ColorSquare(QWidget):
    def __init__(self, color: str):
        super().__init__()
        # Stretch to fill grid cell
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Set background color
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background-color: {color};")

class ExpandingButton(QPushButton):
    def __init__(self, text: str):
        super().__init__(text)
        # Stretch to fill grid cell
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

class ExpandingTextLabel(QLabel):
    def __init__(self, text: str):
        super().__init__(text)
        # Stretch to fill grid cell
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

class TimeLineContext(QWidget):
    layout: QHBoxLayout
    page_count: ExpandingTextLabel
    remove_op: ExpandingButton
    op_dropdown: QComboBox
    insert_op: ExpandingButton
    iteration_idx: ExpandingTextLabel
    insert = pyqtSignal(str)
    remove = pyqtSignal()

    def __init__(self, page_count):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.page_count = ExpandingTextLabel(f"Panel: 1 / {page_count}")
        self.remove_op = ExpandingButton("-")
        self.op_dropdown = QComboBox()
        self.op_dropdown.addItems((label for label in operations.VisOp.registry.keys()))
        self.insert_op = ExpandingButton("+")
        self.iteration_idx = ExpandingTextLabel("Iteration: 0/0")
        self.iteration_idx.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.layout.addWidget(self.page_count, stretch=10)
        self.layout.addWidget(self.remove_op, stretch=5)
        self.layout.addWidget(self.op_dropdown, stretch=70)
        self.layout.addWidget(self.insert_op, stretch=5)
        self.layout.addWidget(self.iteration_idx, stretch=10, alignment=Qt.AlignmentFlag.AlignRight)

    #TODO split UI into 2 labels 1 for page count and 1 for index
    def updatePageCount(self, index: int, page_count: int):
        self.page_count.setText(f"Panel: {index + 1} / {page_count}") 


class NavigationControls(QWidget):
    layout: QHBoxLayout
    left_arrow: ExpandingButton
    right_arrow: ExpandingButton
    up_arrow: ExpandingButton
    down_arrow: ExpandingButton
    next = pyqtSignal()
    previous = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)
        #create arrow keys
        self.left_arrow = ExpandingButton("←")
        self.left_arrow.clicked.connect(self.previous)
        self.right_arrow = ExpandingButton("→")
        self.right_arrow.clicked.connect(self.next)
        self.up_arrow = ExpandingButton("↑")
        self.down_arrow = ExpandingButton("↓")

        #create middle layout
        up_down = QVBoxLayout()
        up_down.addWidget(self.up_arrow)
        up_down.addWidget(self.down_arrow)
        up_down.setSpacing(1)
        up_down.setContentsMargins(5, 2, 5, 2)

        self.layout.addWidget(self.left_arrow, stretch=10)
        self.layout.addLayout(up_down, stretch=80)
        self.layout.addWidget(self.right_arrow, stretch=10)

class TimeLineApplicationView(QWidget):
    layout: QVBoxLayout
    timeline_context: TimeLineContext
    panel_frame: QLabel
    navigation_controls: NavigationControls
    index: int
    page_count: int
    request_page = pyqtSignal(int)
    insert_op = pyqtSignal(str)
    remove_op = pyqtSignal()
    #viewport_changed = pyqtSignal(tuple(int,int))

    def __init__(self, page_count, scaled_resolution: Tuple[int,int]):
        super().__init__()
        self.index = 0
        self.page_count = page_count
        self.layout = QVBoxLayout(self)
        self.timeline_context = TimeLineContext(self.page_count)
        frame_w, frame_h = scaled_resolution
        self.panel_frame = QLabel()
        self.panel_frame.setFixedSize(frame_w, frame_h)
        self.panel_frame.setScaledContents(False)
        self.panel_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.navigation_controls = NavigationControls()
        self.navigation_controls.next.connect(self.onNext)
        self.navigation_controls.previous.connect(self.onPrevious)
        self.layout.addWidget(self.timeline_context, stretch=5)
        self.layout.addWidget(self.panel_frame, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.navigation_controls, stretch=10)

    def displayPixmap(self, image: QImage):
        pixmap = QPixmap().fromImage(image)
        self.panel_frame.setPixmap(pixmap)

    def onNext(self):
        if self.index >= self.page_count - 1:
            return 0
        
        self.index += 1
        self.timeline_context.updatePageCount(self.index, self.page_count)
        self.request_page.emit(self.index)

    def onPrevious(self):
        if not self.index > 0:
            return 0
        
        self.index -= 1
        self.timeline_context.updatePageCount(self.index, self.page_count)
        self.request_page.emit(self.index)

    def keyPressEvent(self, event):

        if event.key() == Qt.Key.Key_Right:
            self.onNext()
            QCoreApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

        elif event.key() == Qt.Key.Key_Left:
            self.onPrevious()
            QCoreApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
            
        else:
            super().keyPressEvent(event)

def print_debug_image(image, panel_frame):
    # 1. Get the actual pixel dimensions (Physical)
    phys_w = image.width()
    phys_h = image.height()
    
    # 2. Get the scaling factor currently attached to the image
    dpr = image.devicePixelRatio()
    
    # 3. Calculate the size Qt uses for layout (Logical)
    # If dpr is 2.0, a 2000px image has a 1000px logical size
    logic_w = phys_w / dpr
    logic_h = phys_h / dpr

    print(f"--- UI DISPLAY DEBUG ---")
    print(f"  - QLabel Size:    {panel_frame.width()}x{panel_frame.height()}")
    print(f"  - Image Physical: {phys_w}x{phys_h}")
    print(f"  - Image DPR:      {dpr}")
    print(f"  - Image Logical:  {logic_w}x{logic_h}")