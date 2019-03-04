import cv2

from combine.segmentation_combine import segmentation_board as segmentation

# put template at the second argument if you have one
img = cv2.imread("D:\cb\cbfolder\(1).jpg")
template, coordinate = segmentation(img)
cv2.imwrite('template.jpg', template)

img = cv2.imread("D:\cb\cbfolder\(4).jpg")
board, coordinate = segmentation(img, template)
cv2.imwrite('4.jpg', board)

img = cv2.imread("D:\cb\cbfolder\(5).jpg")
board, coordinate = segmentation(img, template, coordinate)
cv2.imwrite('5.jpg', board)

