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
from DatasheetExtractor.backend.pdf.page import Direction
from DatasheetExtractor.backend.extractor.pinout import PinoutExtractor

from rtree import index

####################################################################################################

url = 'http://ww1.microchip.com/downloads/en/DeviceDoc/AVR128DA48-Curiosity-Nano-UG-DS50002971A.pdf'
path = Path('.', 'devices', 'AVR128DA48-Curiosity-Nano-UG-DS50002971B.pdf')
url = path
print(url)

document = PdfDocument(url, cache_path='devices')

####################################################################################################

page_number = 24
page = document[page_number]
page_width = page.width
legend_box = page.percent_bbox((60, 80), (30, 38))
pinout_box = page.percent_bbox((18, 91), (38, 77))

# extractor = PinoutExtractor(document[page])
# print()
# print(extractor.format_pinout(extractor.extract_pinout()))

box_index = index.Index()
for i, _ in enumerate(page.color_boxes()):
    # obj=_
    box_index.insert(i, _.bounding_box)

for y in page.sort_xy(
        axe='y',
        use_center1=True,
        use_center2=True,
        ensure_direction=Direction.horizontal,
        # round_scale=page_width/10,
):
    print('---')
    right_side = False
    for line in y:
        if not right_side and line.center_x > page_width / 2:
            print('|')
            right_side = True
        print(line)
        print(line.bbox)
        # print(line.text)
