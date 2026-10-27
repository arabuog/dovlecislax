"""Screen-space candidate detection; deliberately independent of Windows input."""
import cv2
import numpy as np


def detect(frame):
    h, w = frame.shape[:2]
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array((10, 155, 200)), np.array((26, 255, 255)))
    # Ignore sky, minimap, notifications, and player/foreground interaction area.
    mask[:int(h * .29)] = 0
    mask[int(h * .76):] = 0
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for contour in contours:
        x, y, bw, bh = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        if (area >= max(35, w * h * .000035)
                and .65 <= bw / max(bh, 1) <= 2.8
                and area / (bw * bh) >= .55
                and bw < w * .18 and bh < h * .15):
            boxes.append((x, y, bw, bh))
    return sorted(boxes, key=lambda b: b[1] + b[3], reverse=True)
