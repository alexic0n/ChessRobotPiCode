import cv2
from segmentation.segmentation_analysis import segmentation_board as edgeAnalysis
from segmentation.segmentation_find_chess_board_corner import segmentation_board as findCorners
from segmentation.segmentation_template_matching import segmentation_board as templateMatch

image = cv2.imread("segmentation/testImages/google1.jpg")
template = cv2.imread("segmentation/tesplate.jpg")

print(edgeAnalysis(image))
print(findCorners(image))

# error 
# print(templateMatch(image, template))
