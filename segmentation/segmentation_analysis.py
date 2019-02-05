import cv2
import numpy as np


# help function 1: smooth histogram
def his_smooth(his, step):
    length = len(his)
    smooth = np.zeros(length)
    for i in range(step, length - step):
        smooth[i] = sum(his[i - step:i + step + 1]) / (step * 2 + 1)

    return smooth


# help function 2: get boundary of the chessboard with the peaks and bottoms of histogram
def locate_boundary(peaks, bottoms, gape, step_peak, step_bottom):
    length = len(peaks)

    b1 = b2 = 0

    if length < 8:
        return [-2, -2]

    for i in range(0, length - 8):
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


# segmentation function
def segmentation_board(image):
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

    sum_vertical = his_smooth(img_edge.sum(1), d)
    sum_horizontal = his_smooth(img_edge.sum(0), d)

    # 4: get peaks and bottom

    k1 = 1
    k2 = 1

    while 1:

        while 1:

            k1 = k1 * 2

            peaks_horizontal = []
            bottom_horizontal = []

            meter = max(sum_horizontal) / k1

            low = 0
            high = 0
            peak = 0
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

            k2 = k2 * 2

            peaks_vertical = []
            bottom_vertical = []

            meter = max(sum_horizontal) / k2

            low = 0
            high = 0
            peak = 0
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
                return [0, 0, 0, 0]

        # 5: calculate the possible wide of the grid

        max_wide = int(min(w, h) / 8)

        gap_frequent = np.zeros(int(max_wide * 1.1))

        for i in range(0, len(peaks_horizontal)):
            for j in range(i, len(peaks_horizontal)):
                if (peaks_horizontal[j] - peaks_horizontal[i]) > max_wide:
                    break
                if j != i:
                    gap_frequent[peaks_horizontal[j] - peaks_horizontal[i]] = gap_frequent[
                                                                                  peaks_horizontal[j] -
                                                                                  peaks_horizontal[
                                                                                      i]] + 1

        for i in range(0, len(peaks_vertical)):
            for j in range(i, len(peaks_vertical)):
                if (peaks_vertical[j] - peaks_vertical[i]) > max_wide:
                    break
                if j != i:
                    gap_frequent[peaks_vertical[j] - peaks_vertical[i]] = gap_frequent[
                                                                              peaks_vertical[j] - peaks_vertical[i]] + 1

        gap_frequent = his_smooth(gap_frequent, int(len(gap_frequent) / 24))

        gape = np.argmax(gap_frequent)

        # 6: locate the boundary

        bottom_step = w * 255

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

        return [boundary_horizontal[0], boundary_horizontal[1], boundary_vertical[0], boundary_vertical[1]]
