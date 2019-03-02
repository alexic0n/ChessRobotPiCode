import cv2
from segmentation_combine import segmentation_board as segmentation


# put template at the second argument if you have one
img = cv2.imread("D:\cb\c2.jpg")
template, coordinate = segmentation(img)
cv2.imshow('template', template)
cv2.waitKey(0)

img = cv2.imread("D:\cb\c9.jpg")
board, coordinate = segmentation(img, template)
cv2.imshow('board with chess', board)
cv2.waitKey(0)