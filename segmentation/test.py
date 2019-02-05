print("importing modules...", end="\r")

import cv2
from segmentation_analysis import segmentation_board as edgeAnalysis
from segmentation_find_chess_board_corner import segmentation_board as findCorners
from segmentation_template_matching import segmentation_board as templateMatch
print("importing modules... done.")

img = cv2.imread("testImages/felix.jpg")
template = cv2.imread("template.jpg")

print("performing edge detection & analysis...", end="\r")
output = edgeAnalysis(img)
cv2.rectangle(img, (output[0][0], output[0][1]), (output[1][0], output[1][1]), (255,0,0), 2)
cv2.imshow('result', img)
cv2.waitKey(0)
print("performing edge detection & analysis... done.")

print("performing findChessboardCorners...", end="\r")
output = findCorners(img)
cv2.rectangle(img, (output[0][0], output[0][1]), (output[1][0], output[1][1]), (0,255,0), 2)
cv2.imshow('result', img)
cv2.waitKey(0)
print("performing findChessboardCorners... done.")

print("performing template matching...", end="\r")
output = templateMatch(img,template)
cv2.rectangle(img, (output[0][0], output[0][1]), (output[1][0], output[1][1]), (0,0,255), 2)
cv2.imshow('result', img)
cv2.waitKey(0)
print("performing template matching... done.")

