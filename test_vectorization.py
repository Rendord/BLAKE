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
panelPath_2 = Path("manga_scans/jp2/BLAME!_Master_Edition_v01__0000.jp2")

img = cv2.imread(str(panelPath), cv2.IMREAD_GRAYSCALE)
img_2 = cv2.imread(str(panelPath_2), cv2.IMREAD_GRAYSCALE)

b, w = cv2.split(img)


#KERNEL
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

# Rotate first (example: slight deskew)
retval, bw_img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)


ink_img = 255 - bw_img

#ink_open = cv2.morphologyEx(ink_img, cv2.MORPH_OPEN, kernel, iterations=1)
ink_clean = cv2.morphologyEx(ink_img, cv2.MORPH_CLOSE, kernel, iterations=2)


scale = 0.3
h, w = img.shape[:2]
resized = cv2.resize(ink_clean, (int(w * scale), int(h * scale)))
resized_2 = cv2.resize(img_2, (int(w * scale), int(h * scale)))

#rotate using custom function rotates just the image while keeping hxw of original array
img_rotated = rotate_image(resized, angle_deg=90.0)

#rotate using OpenCV built-in for comparison (rotates window because it changes width and height dimensions)
img_rotated_cv = cv2.rotate(resized, cv2.ROTATE_90_CLOCKWISE)



#TODO build a comparison display that holds several images side by to see modification steps
# Make a panel class that holds a list of operations
# When rendering we display the steps side by side in the order we applied them
# what we can do is create overrided methods for each CV2 operation
# we track the image in every state and then we call a display method that shows them
# in the same window

#TODO build a little UI to flick through manga pages and apply operations interactively
#we need some kind of state machine for this and a keylistener
# we want to be able to apply operations and split the window so we can perform
# a couple operations and then split at that stage and then continue applying operations to the second panel

#CLASS

#PANEL SESSION
#OPERATIONS -> LINKED LIST? 
#image path

#ABSTRACT METHOD -> VISUAL OP
# performs visual operation and adds it to the linked list
# operations can be dictionaries or their own class 
# kwaargs or something similar

#METHOD side-by-side
# creates a list of images that consist of each operation of the visual operations linked list in order
# spawns a regular openCV window with all images concatted next to each other



#CLASS view

#this class has a panel session and handles rendering and updating of the panel after operations
# use a small UI framework


print(img.dtype, img.shape, img.min(), img.max())
print("retval threshhold used:", retval)

cv2.imshow("Panel", resized)

cv2.imshow("Unaffected", resized_2)
cv2.waitKey(0)
cv2.destroyAllWindows()
