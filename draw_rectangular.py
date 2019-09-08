

import cv2
import numpy as np

img = cv2.imread("im.jpg")
roi = img[137: 222, 292: 395]
x = 292
y = 137
width = 395 - x
height = 222 - y
hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
roi_hist = cv2.calcHist([hsv_roi], [0], None, [180], [0, 180])
# cap = cv2.VideoCapture(0)
term_criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
cap=cv2.VideoCapture('1.mp4')
while True:
    _, frame = cap.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)
    ret, track_window = cv2.CamShift(mask, (x, y, width, height), term_criteria)
    print(x)

    pts = cv2.boxPoints(ret)
    print(pts[0])
    pts = np.int0(pts)
    cv2.polylines(frame, [pts], True, (255, 0, 0), 2)
    cv2.imshow("mask", mask)
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1)
    if key == 27:
        break
cap.release()
cv2.destroyAllWindows()
