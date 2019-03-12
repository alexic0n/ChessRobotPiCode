import cv2
import numpy as np

def segmentation_board(image_color, template_color=[], previous_coordinate=[]):
    # when there is no template
    if len(template_color) == 0:
        output = segmentation_analysis(image_color)
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


def check_line_v(image):

    his = image.sum(1)

    if max(his) > his.mean(0) * 2:
        return True
    else:
        return False


def check_line_h(image):

    his = image.sum(0)

    if max(his) > his.mean(0) * 2:
        return True
    else:
        return False


# help function: check perpendicular lines
def check_gape(edge, gape, direction):

    if direction == 0:
        size = len(edge[0])
    else:
        size = len(edge)

    output = 0

    number = int(size/gape)

    if direction == 0:
        for i in range(1, number):
            if check_line_h(edge[:,int((i-1/3)*gape):int((i+1/3)*gape)]):
                output += 1
    else:
        for i in range(1, number):
            if check_line_v(edge[int((i-1/3)*gape):int((i+1/3)*gape),:]):
                output += 1

    print(output)

    return output


# help function: figure out the boundary of board from frequency diagram
def locate_boundary(peaks, bottoms, gape, step_peak, step_bottom):
    length = len(peaks)
    grid = 6

    b1 = b2 = 0

    if length < grid:
        return [-2, -2]

    for i in range(0, length - grid):

        if peaks[i] <= gape:
            continue

        # if not check_gape(edge[:, peaks[i] - gape:peaks[i]], gape, direction):
        #     print("reject")
        #     continue

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

            if count == grid:
                b1 = peaks[i]
                b2 = peaks[j]
                break

        if count == grid:
            break

    return [b1, b2]


def segmentation_analysis(image):
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

    cv2.imwrite("Image.jpg", img_edge)
    cv2.waitKey(0)

    # 3: summing the edge and smooth the graph

    sum_vertical = his_smooth(img_edge.sum(1), 0)
    sum_horizontal = his_smooth(img_edge.sum(0), 0)

    k1 = 1
    k2 = 1

    while 1:

        # 4: get peaks and bottom
        while 1:

            print(k1)

            k1 = np.math.ceil(2 * k1)

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

            if len(peaks_horizontal) >= 7:
                break

            if len(peaks_horizontal) < 7 and k1 >= 64:
                return [[0, 0], [0, 0]]

        while 1:

            k2 = np.math.ceil(2 * k2)

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
                    gap_frequent[peaks_horizontal[j] - peaks_horizontal[i]] = gap_frequent[peaks_horizontal[j] -
                                                                                           peaks_horizontal[i]] + 1

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
            if (locate_boundary(peaks_horizontal, bottom_horizontal, gape, peak_step, bottom_step))[0] != 0:
                while 1:
                    bottom_step = int(bottom_step * 2 / 3)
                    output2 = locate_boundary(peaks_horizontal, bottom_horizontal, gape, peak_step, bottom_step)
                    if output2[0] == 0:
                        bottom_step *= 3 / 2
                        break
                break

        boundary_horizontal = locate_boundary(peaks_horizontal, bottom_horizontal, gape, peak_step, bottom_step)

        bottom_step = h * 255

        # 6.2 adjust bottom step and peak step of vertical
        for peak_step in range(1, int(max_wide / 4) + 1):
            if (locate_boundary(peaks_vertical, bottom_vertical, gape, peak_step, bottom_step))[0] != 0:
                while 1:
                    bottom_step = int(bottom_step * 2 / 3)
                    output2 = locate_boundary(peaks_vertical, bottom_vertical, gape, peak_step, bottom_step)
                    if output2[0] == 0:
                        bottom_step *= 3 / 2
                        break
                break

        boundary_vertical = locate_boundary(peaks_vertical, bottom_vertical, gape, peak_step, bottom_step)

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

        # 8 check out line

        # 9: check the ratio of the boundaries
        if 0.8 > (boundary_horizontal[1] - boundary_horizontal[0]) / (
                    boundary_vertical[1] - boundary_vertical[0]) or 1.2 < (
                    boundary_horizontal[1] - boundary_horizontal[0]) / (
                    boundary_vertical[1] - boundary_vertical[0]):
            return [[0, 0], [0, 0]]

        # 10: if there is acceptable output, return the values

        if boundary_horizontal[0] > gape:

            if boundary_horizontal[1] < (h - gape):

                if check_gape(img_edge[boundary_vertical[0]:boundary_vertical[1], boundary_horizontal[0] - gape:boundary_horizontal[0]], gape, 1) \
                        > check_gape(img_edge[boundary_vertical[0]:boundary_vertical[1], boundary_horizontal[1]:boundary_horizontal[1]+gape], gape, 1):
                    boundary_horizontal[0] = boundary_horizontal[0] = boundary_horizontal[0] - gape
                else:
                    boundary_horizontal[1] = boundary_horizontal[1] + gape
            else:
                boundary_horizontal[0] = boundary_horizontal[0] = boundary_horizontal[0] - gape
        else:
            boundary_horizontal[1] = boundary_horizontal[1] + gape

        if boundary_vertical[0] > gape:
            if boundary_vertical[1] < w - gape:
                if check_gape(img_edge[boundary_vertical[0] - gape:boundary_vertical[0], boundary_horizontal[0]:boundary_horizontal[1]], gape, 0) \
                        > check_gape(img_edge[boundary_vertical[1]:boundary_vertical[1]+gape, boundary_horizontal[0]:boundary_horizontal[1]], gape, 0):
                    boundary_vertical[0] = boundary_vertical[0] = boundary_vertical[0] - gape
                else:
                    boundary_vertical[1] = boundary_vertical[1] + gape
            else:
                boundary_vertical[0] = boundary_vertical[0] = boundary_vertical[0] - gape
        else:
            boundary_vertical[1] = boundary_vertical[1] + gape

        if boundary_horizontal[0] > gape:

            if boundary_horizontal[1] < (h - gape):

                if check_gape(img_edge[boundary_vertical[0]:boundary_vertical[1], boundary_horizontal[0] - gape:boundary_horizontal[0]], gape, 1) \
                        > check_gape(img_edge[boundary_vertical[0]:boundary_vertical[1], boundary_horizontal[1]:boundary_horizontal[1]+gape], gape, 1):
                    boundary_horizontal[0] = boundary_horizontal[0] = boundary_horizontal[0] - gape
                else:
                    boundary_horizontal[1] = boundary_horizontal[1] + gape
            else:
                boundary_horizontal[0] = boundary_horizontal[0] = boundary_horizontal[0] - gape
        else:
            boundary_horizontal[1] = boundary_horizontal[1] + gape

        if boundary_vertical[0] > gape:
            if boundary_vertical[1] < w - gape:
                if check_gape(img_edge[boundary_vertical[0] - gape:boundary_vertical[0], boundary_horizontal[0]:boundary_horizontal[1]], gape, 0) \
                        > check_gape(img_edge[boundary_vertical[1]:boundary_vertical[1]+gape, boundary_horizontal[0]:boundary_horizontal[1]], gape, 0):
                    boundary_vertical[0] = boundary_vertical[0] = boundary_vertical[0] - gape
                else:
                    boundary_vertical[1] = boundary_vertical[1] + gape
            else:
                boundary_vertical[0] = boundary_vertical[0] = boundary_vertical[0] - gape
        else:
            boundary_vertical[1] = boundary_vertical[1] + gape

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
