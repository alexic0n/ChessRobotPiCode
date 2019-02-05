import cv2


def segmentation_board(image):
    # 1: calculate terminal criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # 2: transfer image to gray
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 3: resize the image if the image is too large
    w, h = gray.shape[::-1]
    rate = 1

    if (w + h) > 800:
        rate = (800 / (w + h))
        gray = cv2.resize(gray, (0, 0), fx=rate, fy=rate)

    # 2: Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (7, 7), None)

    # 3: if find, output the point. if not, return [[0, 0], [0, 0]]
    if ret:
        # 4: rise the accuracy
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

        top_left = corners2[0] - (corners2[42] - corners2[0]) / 6 - (corners2[6] - corners2[0]) / 6
        bottom_right = corners2[48] + (corners2[48] - corners2[6]) / 6 + (corners2[48] - corners2[42]) / 6

        top_left /= rate
        bottom_right /= rate

        return [top_left[0], bottom_right[0]]
    else:
        return [[0, 0], [0, 0]]
