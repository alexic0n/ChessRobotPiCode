import cv2
from segmentation_analysis import segmentation_board as edgeAnalysis
from segmentation_find_chess_board_corner import segmentation_board as findCorners
from segmentation_template_matching import segmentation_board as templateMatch

img = cv2.imread('D:\d3.jpg')
template = cv2.imread('D:\cbtemplate.jpg')

output = edgeAnalysis(img)
cv2.rectangle(img, (output[0][0], output[0][1]), (output[1][0], output[1][1]), (255,0,0), 2)
cv2.imshow('result', img)
cv2.waitKey(0)

output = findCorners(img)
cv2.rectangle(img, (output[0][0], output[0][1]), (output[1][0], output[1][1]), (0,255,0), 2)
cv2.imshow('result', img)
cv2.waitKey(0)

output = templateMatch(img,template)
cv2.rectangle(img, (output[0][0], output[0][1]), (output[1][0], output[1][1]), (0,0,255), 2)
cv2.imshow('result', img)
cv2.waitKey(0)

