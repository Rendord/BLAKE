import cv2
from pathlib import Path
import numpy as np


def rotate_image(img: np.ndarray, angle_deg: float) -> np.ndarray:
    """
    Rotate an image around its center by angle_deg degrees.
    Keeps original dimensions.
    """
    h, w = img.shape[:2]
    center = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D(center, angle_deg, 1.0)
    rotated = cv2.warpAffine(
        img,
        M,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE
    )
    return rotated


panelPath = Path("manga_scans/jp2/BLAME!_Master_Edition_v01__0000.jp2")

img = cv2.imread(str(panelPath), cv2.IMREAD_GRAYSCALE)

# Rotate first (example: slight deskew)


scale = 0.3
h, w = img.shape[:2]
resized = cv2.resize(img, (int(w * scale), int(h * scale)))

#rotate using custom function rotates just the image while keeping hxw of original array
img_rotated = rotate_image(resized, angle_deg=90.0)

#rotate using OpenCV built-in for comparison (rotates window because it changes width and height dimensions)
img_rotated_cv = cv2.rotate(resized, cv2.ROTATE_90_CLOCKWISE)

cv2.imshow("Panel", img_rotated_cv)
cv2.waitKey(0)
cv2.destroyAllWindows()
