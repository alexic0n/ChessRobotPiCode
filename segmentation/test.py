print("importing modules...")
import time
start = time.time()
import cv2
from segmentation_analysis import segmentation_board as edgeAnalysis
from segmentation_find_chess_board_corner import segmentation_board as findCorners
from segmentation_template_matching import segmentation_board as templateMatch
end = time.time()
print(f"done. ({end - start})\n")

img = cv2.imread("testImages/felix.jpg")
template = cv2.imread("template.jpg")

print("performing edge detection & analysis...")
start = time.time()
output = edgeAnalysis(img)
end = time.time()
cv2.rectangle(img, (output[0][0], output[0][1]), (output[1][0], output[1][1]), (255,0,0), 2)
cv2.imshow('result', img)
cv2.waitKey(0)
print(f"done. ({end - start})\n")

print("performing findChessboardCorners...")
start = time.time()
output = findCorners(img)
end = time.time()
cv2.rectangle(img, (output[0][0], output[0][1]), (output[1][0], output[1][1]), (0,255,0), 2)
cv2.imshow('result', img)
cv2.waitKey(0)
print(f"done. ({end - start})\n")

print("performing template matching...")
start = time.time()
output = templateMatch(img,template)
end = time.time()
cv2.rectangle(img, (output[0][0], output[0][1]), (output[1][0], output[1][1]), (0,0,255), 2)
cv2.imshow('result', img)
cv2.waitKey(0)
print(f"done. ({end - start})\n")

