# http://www.mamba-image.org
# https://rtree.readthedocs.io/en/latest
  https://github.com/Toblerity/rtree

####################################################################################################

from pprint import pprint
import sys

import numpy as np
import cv2 as cv

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
pprint(centroids)

label_image = np.zeros(img_bgr.shape, np.uint8)
print(label_image.shape)
for i in range(1, number_of_labels):
    color = np.array(np.random.rand(3)*255, np.uint8)
    for j in range(3):
        label_image[:,:,j] += np.ma.where(labels == i, color[j], np.uint8(0))

print('display')
cv.destroyAllWindows()

cv.imshow('Original', img_bgr)
print('>')
# cv.imshow('Gray', img_gray)
# print('>')
# cv.imshow('Mask', mask)
# print('>')
# cv.imshow('Opening', opening)
# print('>')
cv.imshow('Label', label_image)
print('>')

cv.waitKey(0)
print('>')
