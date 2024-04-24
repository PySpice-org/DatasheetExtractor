####################################################################################################

from DatasheetExtractor import setup_logging
setup_logging()

import logging
logging.info('Start ...')

####################################################################################################

from pprint import pprint
from pathlib import Path

import os

from DatasheetExtractor import PdfDocument, PdfPage

import numpy as np
import cv2 as cv

try:
    import mamba
except ModuleNotFoundError:
    pass

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
        raise NameError('Bad depth')

    # image size
    wi, hi = image.getSize()
    # array size
    ha, wa = array.shape

    # Checking the sizes
    if wa != wi or ha != hi:
        # import mambaCore
        # raiseExceptionOnError(mambaCore.ERR_BAD_SIZE)
        raise NameError('Bad size np HxW %u x %u mamba %u x %u' %(ha, wa, hi, wi))

    # Extracting the data out of the array and filling the image with it
    data = array.tostring()
    image.loadRaw(data)

####################################################################################################

url = 'https://ww1.microchip.com/downloads/aemDocuments/documents/MCU08/ProductDocuments/DataSheets/AVR128DA28-32-48-64-Data-Sheet-40002183C.pdf'
path = Path('.', 'devices', 'AVR128DA28-32-48-64-Data-Sheet-40002183C.pdf')
url = path
print(url)

document = PdfDocument(url, cache_path='devices')
page_number = 18
page_number = 21
page_number = 24
page_number = 30
page_number = 646
page = document[page_number]
image = page.np_pixmap()
print(page.width, page.height)
print(image.shape)
page.to_png('page.png')

# height, width, _ = image.shape
# mimage = mamba.imageMb(width, height, 8)
# Bad size np HxW 792 x 612 mamba 792 x 640
# np2mamba(image[:,:,0], mimage)

# plt.imshow(image)
# plt.show()

# print(mamba.__file__)
orig = mamba.imageMb('page.png')
width, height = orig.getSize()
print(height, width, orig.getDepth())

tmp = mamba.imageMb(width, height, 8)
tmp2 = mamba.imageMb(width, height, 8)
mask1 = mamba.imageMb(width, height, 1)
mask2 = mamba.imageMb(width, height, 1)
out = mamba.imageMb(width, height, 8)
out_b = mamba.imageMb(width, height, 1)
out_b1 = mamba.imageMb(width, height, 1)
out_b2 = mamba.imageMb(width, height, 1)

SE_T = 1
SE_R = 3

if False:
    mamba.linearClose(orig, tmp, SE_R, 10, grid=mamba.SQUARE, edge=mamba.FILLED)
    mamba.sub(tmp, orig, tmp)
    mamba.linearOpen(tmp, out, SE_T, 20, grid=mamba.SQUARE, edge=mamba.FILLED)
    mamba.threshold(out, out_b, 1, 255)

maxima = mamba.imageMb(orig, 1)
# Extract text (page is black )
# mamba.deepMinima(orig, maxima, 50, grid=mamba.HEXAGONAL)
# Extract text and line (page is white )
mamba.maxDynamics(orig, maxima, 1, grid=mamba.HEXAGONAL)
if True: # V
    mamba.negate(maxima, out_b)
    # filter large v area
    mamba.linearOpen(out_b, out_b, SE_T, 20, grid=mamba.SQUARE, edge=mamba.FILLED)
    # close in H
    mamba.linearClose(out_b, out_b, SE_R, 5, grid=mamba.SQUARE, edge=mamba.FILLED)
    # filter in H
    mamba.linearOpen(out_b, mask2, SE_R, 5, grid=mamba.SQUARE, edge=mamba.FILLED)
    mamba.copy(out_b, mask1)
    mamba.build(mask2, mask1)
    # subtract them
    mamba.sub(out_b, mask1, out_b)
    mamba.copy(out_b, out_b1)

if True: # H
    mamba.negate(maxima, out_b)
    # filter hline
    mamba.linearOpen(out_b, out_b, SE_R, 20, grid=mamba.SQUARE, edge=mamba.FILLED)
    # close in both direction
    mamba.linearClose(out_b, out_b, SE_R, 5, grid=mamba.SQUARE, edge=mamba.FILLED)
    # mamba.linearClose(out_b, out_b, SE_T, 3, grid=mamba.SQUARE, edge=mamba.FILLED)
    # filter large v area and reconstruct
    mamba.linearOpen(out_b, mask2, SE_T, 5, grid=mamba.SQUARE, edge=mamba.FILLED)
    mamba.copy(out_b, mask1)
    mamba.build(mask2, mask1)
    # subtract them
    mamba.sub(out_b, mask1, out_b)
    mamba.copy(out_b, out_b2)

mamba.add(out_b1, out_b2, out_b)

# maxima.show()

# tmp2.show()
# out.show()
# mask1.show()
# out_b.show()

orig.show()
out_b1.show()
out_b2.show()
out_b.show()

_ = input()
