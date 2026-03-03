from dataclasses import dataclass
from typing import Protocol
import numpy as np
import cv2


#TODO implement VisOp as Abstract BaseClass so that arguments for apply are enforced in subclasses
class VisOpProtocol(Protocol):
    def apply(self) -> np.ndarray: ...
    def signature(self) -> int: ...

class VisOp(VisOpProtocol):
    registry: dict[str, type["VisOp"]] = {}

    label = ""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls is VisOp:
            return
        name = cls.label or cls.__name__
        if name != "Root": #Needs to be removed ASAP
            VisOp.registry[name] = cls

    @classmethod
    def create(cls, label:str, **kwargs) -> "VisOp":
        return cls.registry[label](**kwargs)

@dataclass(frozen=True)
class ThresholdOp(VisOp):
    """
    Binary thresholding operation.
    """
    threshold_value: int = 128
    strength_multiplier: float = 1.1
    label = "Threshold"

    def apply(self, img: np.ndarray, strength: int) -> np.ndarray:
        if len(img.shape) > 2:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        if strength > 1:
            threshold_value = self.threshold_value * (self.strength_multiplier ** strength)
            print(threshold_value)
        else:
            threshold_value = self.threshold_value 
        _, result = cv2.threshold(img, threshold_value, 255, cv2.THRESH_BINARY)
        return result
    
    def signature(self):
        return hash((self.label, self.threshold_value))

@dataclass(frozen=True)
class MorphOpenOp(VisOp):
    """
    Morphological opening operation (erosion followed by dilation).
    """
    kernel_size: int = 3
    label = "Morph Open"

    def apply(self, img: np.ndarray, strength: int) -> np.ndarray:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (self.kernel_size, self.kernel_size))
        return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel, iterations=strength)
    
    def signature(self):
        return hash((self.label, self.kernel_size))


@dataclass(frozen=True)
class MorphCloseOp(VisOp):
    """
    Morphological closing operation (dilation followed by erosion).
    """
    kernel_size: int = 3
    label = "Morph Close"

    def apply(self, img: np.ndarray, strength: int) -> np.ndarray:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (self.kernel_size, self.kernel_size))
        return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel, iterations=strength)
    
    def signature(self):
        return hash((self.label, self.kernel_size))


@dataclass(frozen=True)
class InvertOp(VisOp):
    """
    Image inversion operation.

    Inverts grayscale values: 255 - pixel_value.
    """
    label = "Invert"

    def apply(self, img: np.ndarray, strength: int) -> np.ndarray:
        return 255 - img
    
    def signature(self):
        return hash(self.label)


