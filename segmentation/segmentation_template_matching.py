import cv2
import numpy as np


def segmentation_board(image_color, template_color):

    # 1: convert to gray image
    image = cv2.cvtColor(image_color, cv2.COLOR_BGR2GRAY)
    template = cv2.cvtColor(template_color, cv2.COLOR_BGR2GRAY)

    # 2: get the degree of blur by the size of image

    d = int((len(image) + len(image[0])) / 400)

    # 3: blur and get edge with abs different

    img_gray = cv2.blur(image, (d, d))

    img_gray = np.array(img_gray, np.int8)
    img_gray_shift = np.roll(img_gray, d, 0)
    img_gray_shift = np.roll(img_gray_shift, d, 1)
    img_edge = np.uint8(np.absolute(img_gray - img_gray_shift))

    # 4: get the size of the template

    w, h = template.shape[::-1]
    iw, ih = image.shape[::-1]
    image_size = min(iw, ih)

    floor = np.math.ceil((w/image_size)*10)/10
    ceil = np.math.floor((2*w/image_size)*10)/10

    compare_method = eval('cv2.TM_CCOEFF_NORMED')

    max_match = 0
    max_rate = 0

    # 5: change the size of image and try matching
    for i in np.arange(floor, ceil, 0.01):

        # 5-1: Apply template Matching
        smaller = cv2.resize(img_edge, (0, 0), fx=i, fy=i)

        res = cv2.matchTemplate(smaller, template, compare_method)

        match_rate = res.max()

        # 5-2: if the match rate is higher than previous one, record it
        if match_rate > max_rate:
            max_rate = match_rate

            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            # 5-3: record the coordinate of top_left corner and the ratio of resize
            top_left_smaller = max_loc
            max_match = i

    # 6: convert the coordinate to the original size

    top_left = [int((top_left_smaller[0]/max_match)), int((top_left_smaller[1]/max_match))]

    bottom_right = [(top_left[0] + int(w/max_match)), (top_left[1] + int(h/max_match))]

    return [top_left, bottom_right]
