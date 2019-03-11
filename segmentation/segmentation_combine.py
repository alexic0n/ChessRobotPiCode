import cv2
import numpy as np


def segmentation_board(image_color, template_color=[], previous_coordinate=[], is_empty_board=False):
    # when there is no template
    if len(template_color) == 0:
        output = segmentation_analysis(image_color, is_empty_board)
        template = image_color[output[0][1]:output[1][1], output[0][0]:output[1][0]]
        return template, output
    # when there is template
    else:
        output = segmentation_template(image_color, template_color)

        # if previous coordinate has not been provided
        if len(previous_coordinate) == 0:
            board = image_color[output[0][1]:output[1][1], output[0][0]:output[1][0]]
            return board, output

        else:
            output2 = segmentation_analysis(image_color)

            if distance_between(output[0], output2[0]) < (len(template_color) / 8) * (len(template_color) / 8):
                board = image_color[output[0][1]:output[1][1], output[0][0]:output[1][0]]
                return board, output
            else:
                board = image_color[previous_coordinate[0][1]:previous_coordinate[1][1],
                        previous_coordinate[0][0]:previous_coordinate[1][0]]
                return board, previous_coordinate


# help function: find square of distance between coordinates
def distance_between(c1, c2):
    return (c1[0] - c2[0]) * (c1[0] - c2[0]) + (c1[1] - c2[1]) * (c1[1] - c2[1])


# help function: smooth histogram
def his_smooth(his, step):
    length = len(his)
    smooth = np.zeros(length)
    for i in range(step, length - step):
        smooth[i] = sum(his[i - step:i + step + 1]) / (step * 2 + 1)

    return smooth


# help function: figure out the boundary of board from frequency diagram
def locate_boundary(peaks, bottoms, gape, step_peak, step_bottom, start_point=0):
    length = len(peaks)

    b1 = b2 = 0

    if length < 8:
        return [-2, -2]

    for i in range(0, length - 8):

        if peaks[i] <= start_point:
            continue

        pointer = i
        count = 0
        last_bottom = -1
        for j in range(i + 1, length):

            if (gape - step_peak) <= (peaks[j] - peaks[pointer]) <= (gape + step_peak):

                if last_bottom != -1:
                    last_bottom = min(bottoms[j - 1], last_bottom)
                else:
                    last_bottom = bottoms[pointer]

                if count != 0:

                    if abs(last_bottom - bottoms[pointer - 1]) <= step_bottom:
                        pointer = j
                        count += 1
                else:
                    pointer = j
                    count += 1

            if (peaks[j] - peaks[pointer]) > (gape + step_peak):
                break

            if count == 8:
                b1 = peaks[i]
                b2 = peaks[j]
                break

        if count == 8:
            break

    return [b1, b2]


# check if the empty board is acceptable
# return 0: acceptable 1: invalid vertical boundary 2: invalid horizontal boundary 3: invalid for both boundary
def boundary_check(image, h0, v0, h8, v8):
    h = h8 - h0
    v = v8 - v0

    threshold = 60

    h1 = int(h0 + h * 1 / 8)
    h2 = int(h0 + h * 2 / 8)
    h3 = int(h0 + h * 3 / 8)
    h4 = int(h0 + h * 4 / 8)
    h5 = int(h8 - h * 3 / 8)
    h6 = int(h8 - h * 2 / 8)
    h7 = int(h8 - h * 1 / 8)

    v1 = int(v0 + v * 1 / 8)
    v2 = int(v0 + v * 2 / 8)
    v3 = int(v0 + v * 3 / 8)
    v4 = int(v0 + v * 4 / 8)
    v5 = int(v8 - v * 3 / 8)
    v6 = int(v8 - v * 2 / 8)
    v7 = int(v8 - v * 1 / 8)

    hw = (image[v1:v2, h0:h1].mean(0).mean(0) + image[v5:v6, h0:h1].mean(0).mean(0)) / 2
    hb = (image[v2:v3, h0:h1].mean(0).mean(0) + image[v4:v5, h0:h1].mean(0).mean(0) + image[v6:v7, h0:h1].mean(0).mean(
        0)) / 3
    hc = (image[v3:v4, h0:h1].mean(0).mean(0) + image[v7:v8, h0:h1].mean(0).mean(0)) / 2

    vw = (image[v0:v1, h1:h2].mean(0).mean(0) + image[v0:v1, h5:h6].mean(0).mean(0)) / 2
    vb = (image[v0:v1, h2:h3].mean(0).mean(0) + image[v0:v1, h4:h5].mean(0).mean(0) + image[v0:v1, h6:h7].mean(0).mean(
        0)) / 3
    vc = (image[v0:v1, h3:h4].mean(0).mean(0) + image[v0:v1, h7:h8].mean(0).mean(0)) / 2

    if np.absolute((hb - hc).sum(0)) - np.absolute((hw - hc).sum(0)) > threshold:
        if np.absolute((vb - vc).sum(0)) - np.absolute((vw - vc).sum(0)) > threshold:
            return 0
        else:
            return 1
    else:
        if np.absolute((vb - vc).sum(0)) - np.absolute((vw - vc).sum(0)) > threshold:
            return 2
        else:
            return 3


# segmentation function: analysis
def segmentation_analysis(image, is_empty_board=False):
    # 1: convert image to gray and get the size of the image

    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    w = len(img_gray)
    h = len(img_gray[0])
    d = int((w + h) / 400)

    # 2: blur and get edge with abs different

    img_gray = cv2.blur(img_gray, (d, d))

    img_gray = np.array(img_gray, np.int8)
    img_gray_shift = np.roll(img_gray, d, 0)
    img_gray_shift = np.roll(img_gray_shift, d, 1)
    img_edge = np.uint8(np.absolute(img_gray - img_gray_shift))

    # 3: summing the edge and smooth the graph

    sum_vertical = his_smooth(img_edge.sum(1), 0)
    sum_horizontal = his_smooth(img_edge.sum(0), 0)

    k1 = 1
    k2 = 1

    start_point_vertical = 0
    start_point_horizontal = 0

    while 1:

        # 4: get peaks and bottom
        while 1:

            k1 = np.math.ceil(1.5 * k1)

            if k1 > 100:
                return [[0, 0], [0, 0]]

            peaks_horizontal = []
            bottom_horizontal = []

            meter = max(sum_horizontal) / k1

            low = sum_horizontal[0]
            high = sum_horizontal[0]
            peak = -1
            bottom = 0

            for i in range(1, h):

                if (sum_horizontal[i] - low) > meter:
                    if peak < bottom:
                        high = sum_horizontal[i]
                        peak = i
                        bottom_horizontal.append(sum_horizontal[bottom])

                    if sum_horizontal[i] > high:
                        high = sum_horizontal[i]
                        peak = i

                if (high - sum_horizontal[i]) > meter:
                    if bottom < peak:
                        low = sum_horizontal[i]
                        bottom = i
                        peaks_horizontal.append(peak)
                    if sum_horizontal[i] < low:
                        low = sum_horizontal[i]
                        bottom = i

            if len(peaks_horizontal) >= 9:
                break

            if len(peaks_horizontal) < 9 and k1 >= 64:
                return [0, 0, 0, 0]

        while 1:

            k2 = np.math.ceil(1.5 * k2)

            if k2 > 100:
                return [[0, 0], [0, 0]]

            peaks_vertical = []
            bottom_vertical = []

            meter = max(sum_horizontal) / k2

            low = sum_horizontal[0]
            high = sum_horizontal[0]
            peak = -1
            bottom = 0

            for i in range(1, w):

                if (sum_vertical[i] - low) > meter:
                    if peak < bottom:
                        high = sum_vertical[i]
                        peak = i
                        bottom_vertical.append(sum_vertical[bottom])
                    if sum_vertical[i] > high:
                        high = sum_vertical[i]
                        peak = i

                if (high - sum_vertical[i]) > meter:
                    if bottom < peak:
                        low = sum_vertical[i]
                        bottom = i
                        peaks_vertical.append(peak)
                    if sum_vertical[i] < low:
                        low = sum_vertical[i]
                        bottom = i

            if len(peaks_vertical) >= 9:
                break

            if len(peaks_vertical) < 9 and k2 >= 64:
                return [[0, 0], [0, 0]]

        # 5: calculate the possible wide of the grid

        max_wide = int(min(w, h) / 8)
        min_wide = int(min(w, h) / 16)

        gap_frequent = np.zeros(int(max_wide * 1.1))

        for i in range(0, len(peaks_horizontal)):
            for j in range(i, len(peaks_horizontal)):
                if (peaks_horizontal[j] - peaks_horizontal[i]) > max_wide:
                    break
                if j != i and (peaks_horizontal[j] - peaks_horizontal[i]) > min_wide:
                    gap_frequent[peaks_horizontal[j] - peaks_horizontal[i]] = gap_frequent[
                                                                                  peaks_horizontal[j] -
                                                                                  peaks_horizontal[
                                                                                      i]] + 1

        for i in range(0, len(peaks_vertical)):
            for j in range(i, len(peaks_vertical)):
                if (peaks_vertical[j] - peaks_vertical[i]) > max_wide:
                    break
                if j != i and (peaks_vertical[j] - peaks_vertical[i]) > min_wide:
                    gap_frequent[peaks_vertical[j] - peaks_vertical[i]] = gap_frequent[
                                                                              peaks_vertical[j] - peaks_vertical[i]] + 1

        gap_frequent = his_smooth(gap_frequent, int(len(gap_frequent) / 24))

        gape = np.argmax(gap_frequent)

        # 6: locate the boundary

        bottom_step = w * 255

        # 6.1: adjust bottom step and peak step of horizontal
        for peak_step in range(1, int(max_wide / 4) + 1):
            if (
                    locate_boundary(peaks_horizontal, bottom_horizontal, gape, peak_step, bottom_step,
                                    start_point_horizontal))[0] != 0:
                while 1:
                    bottom_step = int(bottom_step * 2 / 3)
                    output2 = locate_boundary(peaks_horizontal, bottom_horizontal, gape, peak_step, bottom_step,
                                              start_point_horizontal)
                    if output2[0] == 0:
                        bottom_step *= 3 / 2
                        break
                break

        boundary_horizontal = locate_boundary(peaks_horizontal, bottom_horizontal, gape, peak_step, bottom_step,
                                              start_point_horizontal)

        bottom_step = h * 255

        # 6.2 adjust bottom step and peak step of vertical
        for peak_step in range(1, int(max_wide / 4) + 1):
            if (locate_boundary(peaks_vertical, bottom_vertical, gape, peak_step, bottom_step, start_point_vertical))[0] != 0:
                while 1:
                    bottom_step = int(bottom_step * 2 / 3)
                    output2 = locate_boundary(peaks_vertical, bottom_vertical, gape, peak_step, bottom_step,
                                              start_point_vertical)
                    if output2[0] == 0:
                        bottom_step *= 3 / 2
                        break
                break

        boundary_vertical = locate_boundary(peaks_vertical, bottom_vertical, gape, peak_step, bottom_step,
                                            start_point_vertical)

        # 7: check if one of the output is empty, change the parameter and run again
        if boundary_horizontal[0] == 0:
            k1 = k1 * 2
            peaks_vertical.clear()
            peaks_horizontal.clear()
            bottom_vertical.clear()
            bottom_horizontal.clear()
            continue

        if boundary_vertical[0] == 0:
            k2 = k2 * 2
            peaks_vertical.clear()
            peaks_horizontal.clear()
            bottom_vertical.clear()
            bottom_horizontal.clear()
            continue

        # 8: check if the segmentation is correct
        if is_empty_board:
            check_result = boundary_check(image, boundary_horizontal[0], boundary_vertical[0], boundary_horizontal[1],
                                          boundary_vertical[1])

            print(check_result)
            if check_result == 1:
                start_point_vertical = boundary_vertical[0] + 1
                print("reject")
                continue
            if check_result == 2:
                start_point_horizontal = boundary_horizontal[0] + 1
                print("reject")
                continue
            if check_result == 3:
                start_point_vertical = boundary_vertical[0] + 1
                start_point_horizontal = boundary_horizontal[0] + 1
                print("reject")
                continue

        # 9: check the ratio of the boundaries
        if 0.8 > (boundary_horizontal[1] - boundary_horizontal[0])/(boundary_vertical[1] - boundary_vertical[0]) or 1.2 < (boundary_horizontal[1] - boundary_horizontal[0]) / (boundary_vertical[1] - boundary_vertical[0]):
            return [[0, 0], [0, 0]]

        # 10: if there is acceptable output, return the values
        return [[boundary_horizontal[0], boundary_vertical[0]], [boundary_horizontal[1], boundary_vertical[1]]]


# segmentation function: template matching
def segmentation_template(image_color, template_color):
    # 1: convert to gray image
    image = cv2.cvtColor(image_color, cv2.COLOR_BGR2GRAY)
    template = cv2.cvtColor(template_color, cv2.COLOR_BGR2GRAY)

    # 2: define the compare_method and get the size of template
    compare_method = eval('cv2.TM_CCOEFF')
    w, h = template.shape[::-1]

    # 3: run template matching
    res = cv2.matchTemplate(image, template, compare_method)

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # 4: get the right down corner
    bottom_right = [(max_loc[0] + w), (max_loc[1] + h)]

    return [max_loc, bottom_right]
