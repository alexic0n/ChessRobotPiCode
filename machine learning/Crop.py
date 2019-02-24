#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2 as cv
from PIL import Image

def crop_squares(path):
    # Crops a given image of a chessboard into 64 squares
    src = cv.imread(path)
    img = Image.open(path)
    pixels = 224
    prW = 0
    prH = 0
    i = 0
    height, width, x = src.shape
    sqH = height / 8
    sqW = width / 8
    k=8
    while (i < 8):
        letter = 'a'
        start = i * 8
        end = (i + 1) * 8

        for j in range(start, end):
            box = (prW, prH, sqW, sqH)
            board = img.crop(box)
            board = board.resize((pixels, pixels), Image.ANTIALIAS)
            # Save the square into the Cropped folder
            board.save(('Logitech webcam/Cropped/{}{}.jpg').format(letter, k))
            prW = sqW
            sqW = sqW + width / 8
            letter = chr(ord(letter) + 1)
        prW = 0
        prH = height / 8 * (i + 1)
        sqW = width / 8
        sqH = height / 8 * (i + 2)
        i = i + 1
        k = k - 1
