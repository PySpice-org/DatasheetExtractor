####################################################################################################

from DatasheetExtractor import setup_logging
setup_logging()

import logging
logging.info('Start ...')

####################################################################################################

from pprint import pprint

import os

from DatasheetExtractor import Document, Page

####################################################################################################

url = 'https://ww1.microchip.com/downloads/aemDocuments/documents/MCU08/ProductDocuments/DataSheets/AVR128DA28-32-48-64-Data-Sheet-40002183C.pdf'

document = Document(url, cache_path='devices')
# document.download()

document._load()

####################################################################################################

# page = document[18]
# array = page.pixmap()
# print(page.width, page.height)
# print(array.shape)

####################################################################################################

# for page in range(14, 17 +1):
#     print()
#     print(f'Page {page}')
#     print(Page.format_pinout(document[page].extract_pinout_quad()))

####################################################################################################

# page = document[2]
# page_width = page.width

# for y in page._sort_xy(axe='x', use_center1=False, use_center2=False, round_scale=200).values():
#     print('---')
#     for line in y:
#         # print(line)
#         print(line.text)

# for y in page._sort_xy(axe='y', use_center=True, round_scale=page_width/10).values():
#     print('---')
#     for line in y:
#         # print(line)
#         print(line.text)

####################################################################################################

# page = document[4]
# # for line in page.lines:
# #     print(line)
# for y in page._sort_xy(axe='y', use_center1=True, use_center2=False, round_scale=100).values():
#     text = ''.join(_.text for _ in y)
#     span0 = y[0]
#     print(int(span0.x / span0.size), text)

####################################################################################################

def process_multiplexing_table(page_number):
    page = document[page_number]

    new_lines = []
    previous_line = None
    for line in page.filter_lines(size=4.5):
        # print(line)
        if previous_line is None:
            previous_line = line
            new_lines.append(previous_line)
        else:
            if previous_line.siblings_bbox.enlarge(10).intersect(line.bbox.enlarge(10)):
                previous_line.link(line)
                # print('merge close')
                # print(previous_line)
                # print(line)
            # exponent: merge consecutive lines with x1 < x2 and |y2 - y1| < font size
            # if abs(line.x_min - previous_line.x_max) < line.size and abs(line.y - previous_line.y) < previous_line.size:
            #     previous_line.link(line)
            #     # print('merge exponent')
            #     # print(previous_line)
            #     # print(line)
            # consecutive lines sharing the same x center could be within the same cell
            # check if the merged span has the same y center
            elif abs(line.center_x - previous_line.center_x) < 10:
                previous_line.link(line)
                # print('merge cell')
                # print(previous_line)
                # print(line)
                # print(previous_line.siblings_bbox.center)
            else:
                new_lines.append(line)
                previous_line = line

    rows = []
    previous_line = None
    for line in new_lines:
        if previous_line is not None and abs(line.center_y_inclusive - previous_line.center_y_inclusive) < previous_line.size:
            rows[-1].append(line)
        else:
            rows.append([line])
        previous_line = line

    # for row in rows:
    #     print('-'*10)
    #     for line in row:
    #         text = str(line)
    #         if line.siblings:
    #             sep = ' // '
    #             text += sep + sep.join([_.text for _ in line.siblings])
    #         print(text)

    print('='*50)
    for row in rows[1:]:
        pin_numbers = []
        pin_name = None
        ios = []
        pin = False
        for line in row:
            text = line.text
            if line.siblings:
                sep = ' // '
                text += sep + sep.join([_.text for _ in line.siblings])
            if not pin and abs(line.center_x - Page.to_scaled(126)) < Page.to_scaled(4.5):
                pin_name = text
                pin = True
            elif not pin:
                pin_numbers.append(text)
            else:
                ios.append(text)
        print(pin_name, pin_numbers, ios)

####################################################################################################

for _ in (18, 19):
    process_multiplexing_table(_)
