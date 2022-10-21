# http://www.mamba-image.org
# https://rtree.readthedocs.io/en/latest
#   https://github.com/Toblerity/rtree

####################################################################################################

from pprint import pprint
import sys

import numpy as np
import cv2 as cv

import matplotlib.pyplot as plt

####################################################################################################

img_bgr = cv.imread('p17.png')
img_rgb = cv.cvtColor(img_bgr, cv.COLOR_BGR2RGB)
img_hsv = cv.cvtColor(img_bgr, cv.COLOR_BGR2HSV)
img_gray = cv.cvtColor(img_bgr, cv.COLOR_BGR2GRAY)
# img_gray = cv.inRange(img_gray, 0, 255 -1)
ret, img_gray = cv.threshold(img_gray, 254, 255, cv.THRESH_BINARY_INV)

color = np.array((0, 180, 230))
mask = cv.inRange(img_rgb, color, color)

kernel_size = 10
kernel = cv.getStructuringElement(cv.MORPH_RECT, (kernel_size, kernel_size))
opening = cv.morphologyEx(img_gray, cv.MORPH_OPEN, kernel)

# CV_32S and CV_16U
number_of_labels, labels, stats, centroids = cv.connectedComponentsWithStats(opening, 8, cv.CV_32S)
pprint(number_of_labels)
#pprint(centroids)

label_image = np.zeros(img_bgr.shape, np.uint8)
print(label_image.shape)
for i in range(1, number_of_labels):
    color = np.array(np.random.rand(3)*255, np.uint8)
    for j in range(3):
        label_image[:,:,j] += np.ma.where(labels == i, color[j], np.uint8(0))

cv.imwrite('label.png', labels)

colors = {}
for i in range(1, number_of_labels):
    # mask = labels == i
    # masked = np.ma.masked_array(img_rgb[:,:,0], mask=mask)
    c, r = [int(_) for _ in centroids[i]]
    print()
    print('label', i, r, c)
    size = 5 -1
    # print(labels[r-size:r+size+1, c-size:c+size+1])
    pixel_value = {}
    pixel_count = {}
    for j in range(3):
        view = img_rgb[r-size:r+size+1, c-size:c+size+1, j]
        S = view.size
        # print(view)
        values, count = np.unique(view, return_counts=True)
        data = [(value, int(count/S*100)) for value, count in zip(values, count)]
        data.sort(key=lambda _: _[1], reverse=True)
        data = data[:3]
        # print(data)
        for rank, _ in enumerate(data):
            pixel_count.setdefault(rank, 0)
            pixel_value.setdefault(rank, [])
            pixel_count[rank] += _[1]
            pixel_value[rank].append(_[0])
    for rank in pixel_count.keys():
        count = int(pixel_count[rank] / 3)
        value = '/'.join([str(_) for _ in pixel_value[rank]])
        if count >= 15:
            print(value, count)
            colors.setdefault(value, [])
            colors[value].append(i)
pprint(colors)

# fig = plt.figure()
# ax = fig.add_subplot(1, 2, 1)
# plt.imshow(img_rgb)
# ax = fig.add_subplot(1, 2, 2)
# plt.imshow(label_image)
# plt.show()

# !!!
# cv.imshow('Original', img_bgr)
# cv.imshow('Gray', img_gray)
# cv.imshow('Mask', mask)
# cv.imshow('Opening', opening)
# cv.imshow('Label', label_image)
