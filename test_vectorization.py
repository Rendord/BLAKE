import cv2
from pathlib import Path

panelPath = Path("manga_scans\jp2\BLAME!_Master_Edition_v01__0000.jp2")

img = cv2.imread(str(panelPath), cv2.IMREAD_GRAYSCALE)


scale = 0.3
h, w = img.shape[:2]
resized = cv2.resize(img, (int(w * scale), int(h * scale)))


cv2.imshow("Panel", resized)
cv2.waitKey(0)        # waits for any key
cv2.destroyAllWindows()