####################################################################################################

from DatasheetExtractor import setup_logging
setup_logging()

import logging
logging.info('Start ...')

####################################################################################################

from pprint import pprint

import os

from DatasheetExtractor import Document, Page

import numpy as np
import cv2 as cv

import mamba

import matplotlib.pyplot as plt

####################################################################################################

def mamba2np(image):
    """Creates an 2D array containing the same data as in 'image'. Only works for greyscale and 32-bit
    images. Returns the array.

    """
    if image.getDepth() == 8:
        dtype = np.uint8
    elif image.getDepth() == 32:
        dtype = np.uint32
    else:
        # import mambaCore
        # raiseExceptionOnError(mambaCore.ERR_BAD_DEPTH)
        raise NameError()

    w, h = image.getSize()
    # First extracting the raw data out of image image
    data = image.extractRaw()
    # creating an array with this data
    # At this step this is a one-dimensional array
    array1D = np.fromstring(data, dtype=dtype)
    # Reshaping it to the dimension of the image
    array2D = array1D.reshape((h, w))
    return array2D

def np2mamba(array, image):
    """Fills image 'image' with the content of two dimensional 'array'. Only works for greyscale and
    32-bit images.

    """
    # Checking depth
    if (image.getDepth() == 8 and array.dtype != np.uint8) or \
       (image.getDepth() == 32 and array.dtype != np.uint32) or \
       (image.getDepth() == 1):
        # import mambaCore
        # raiseExceptionOnError(mambaCore.ERR_BAD_DEPTH)
        raise NameError()

    # image size
    wi, hi = image.getSize()
    # array size
    ha, wa = array.shape

    # Checking the sizes
    if wa != wi or ha != hi:
        # import mambaCore
        # raiseExceptionOnError(mambaCore.ERR_BAD_SIZE)
        raise NameError()

    # Extracting the data out of the array and filling the image with it
    data = array.tostring()
    image.loadRaw(data)

####################################################################################################

url = 'https://ww1.microchip.com/downloads/aemDocuments/documents/MCU08/ProductDocuments/DataSheets/AVR128DA28-32-48-64-Data-Sheet-40002183C.pdf'

document = Document(url, cache_path='devices')
document._load()
page = document[14]
image = page.pixmap()
print(page.width, page.height)
print(image.shape)

plt.imshow(image)
plt.show()

# print(mamba.__file__)
# mimage = mamba.imageMb('dev/p17.png')
# print(mimage.getDepth())

# mimage.show()
# _ = input()

# print('imshow')
# cv.imshow('Original', image)
# print('>')

# cv.waitKey(0)
# print('>')
