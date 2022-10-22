#! /usr/bin/env python
# -*- Python -*-

####################################################################################################
#
# Require upgrade
#
####################################################################################################

####################################################################################################

import argparse
import sys

import numpy as np

import Babel.MuPdf as mupdf
import Babel.MuPdf.TextIterator as mupdf_iter

from PyQt5 import QtCore, QtGui, QtWidgets

####################################################################################################

def show_metadata(ctx, doc):

    for key in (
        'Title',
        'Subject',
        'Author',
        'Creator',
        'Producer',
        'CreationDate',
        'ModDate',
        ):
        print(mupdf.decode_utf8(mupdf.get_meta_info(ctx, doc, key, 1024)))

    fz_buffer = mupdf.pdf_metadata(doc)
    print(mupdf.decode_utf8(mupdf.buffer_data(fz_buffer)))
    mupdf.drop_buffer(ctx, fz_buffer)

####################################################################################################

def show_pdf(np_array):

    application = QtWidgets.QApplication(sys.argv)

    height, width = np_array.shape[:2]
    image = QtWidgets.QImage(np_array.data, width, height, QtWidgets.QImage.Format_ARGB32)

    label = QtWidgets.QLabel()
    label.setPixmap(QtWidgets.QPixmap.fromImage(image))

    area = QtWidgets.QScrollArea()
    area.setWidget(label)
    area.setWindowTitle(args.filename)
    area.show()

    application.exec_()

####################################################################################################

def get_font_name(font):

    font_name = mupdf.decode_utf8(mupdf.get_font_name(font))
    i = font_name.find('+')
    if i:
        font_name = font_name[i+1:]

    return font_name

####################################################################################################

def dump_bbox(obj):

    return '[%g %g %g %g]' % (obj.bbox.x0, obj.bbox.y0,
                              obj.bbox.x1, obj.bbox.y1)

####################################################################################################

def dump_text_style(text_sheet):

    style = text_sheet.style
    while style:
        font = style.font
        message = 'span.s%u{font-family:"%s";font-size:%gpt' % (style.id, get_font_name(font), style.size)
        if mupdf.font_is_italic(font):
            message += ';font-style:italic'
        if mupdf.font_is_bold(font):
            message += ';font-weight:bold;'
        message += '}'
        print(message)
        style = style.next

####################################################################################################

def dump_text_page_xml(text_page):

    print('<page>')
    for block in mupdf_iter.TextBlockIterator(text_page):
        print('<block bbox="' + dump_bbox(block) + '">')
        for line in mupdf_iter.TextLineIterator(block):
            print(' '*2 + '<line bbox="' + dump_bbox(line) + '">')
            for span in mupdf_iter.TextSpanIterator(line):
                print(' '*4 + '<span bbox="' + dump_bbox(span) + '" ">')
                for ch in mupdf_iter.TextCharIterator(span):
                    style = ch.style
                    font_name = get_font_name(style.font)
                    print(' '*6 + '<char ' + \
                        ' c="%s" font="%s" size="%g"/>' % (chr(ch.c), font_name, style.size))
                print(' '*4 + '</span>')
            print(' '*2 + '</line>')
        print('</block>')
    print('</page>')

####################################################################################################

def dump_text_page(text_page):

    empty_block = False
    for block in mupdf_iter.TextBlockIterator(text_page):
        if not empty_block:
            print('\n<Block>')
        empty_block = True
        for line in mupdf_iter.TextLineIterator(block):
            line_text = ''
            for span in mupdf_iter.TextSpanIterator(line):
                span_text = ''
                for ch in mupdf_iter.TextCharIterator(span):
                    span_text += chr(ch.c)
                span_text = span_text.rstrip()
                if span_text:
                    line_text += '<Span>' + span_text + '</Span>'
                else:
                    line_text += '<Empty Span>'
            if line_text:
                print(line_text)
                empty_block = False

####################################################################################################

class GrowingTextBrowser(QtWidgets.QTextBrowser):

    _id = 0

    ##############################################

    def __init__(self, *args, **kwargs):

        GrowingTextBrowser._id += 1
        self._id = GrowingTextBrowser._id

        super(GrowingTextBrowser, self).__init__(*args, **kwargs)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        size_policy.setHeightForWidth(True)
        self.setSizePolicy(size_policy)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    ##############################################

    def setPlainText(self, text):

        super(GrowingTextBrowser, self).setPlainText(text)
        self._text = text

    ##############################################

    def print_document_size(self, document=None):

        if document is None:
            document = self.document()
        document_size = document.size()
        print('Document width', document_size.width(), 'height', document_size.height())

    ##############################################

    def sizePolicy(self):

        size_policy = super(GrowingTextBrowser, self).sizePolicy()
        print('GrowingTextBrowser.sizePolicy', self._id, \
            size_policy.horizontalPolicy(), size_policy.verticalPolicy())
        return size_policy

    ##############################################

    def sizeHint(self):

        size = super(GrowingTextBrowser, self).sizeHint()
        print('GrowingTextBrowser.sizeHint', self._id, size.width(), size.height())
        return QtCore.QSize(0, 0)

    ##############################################

    def minimumSizeHint(self):

        size = super(GrowingTextBrowser, self).minimumSizeHint()
        print('GrowingTextBrowser.minimumSizeHint', self._id, size.width(), size.height())
        return QtCore.QSize(0, 0)

    ##############################################

    def heightForWidth(self, width):

        print('GrowingTextBrowser.heightForWidth', self._id, width)
        document = QtWidgets.QTextDocument(self._text)
        document.setPageSize(QtCore.QSizeF(width, -1))
        height = document.documentLayout().documentSize().toSize().height()
        self.print_document_size(document)
        return height + self.font().pointSize()

    ##############################################

    def resizeEvent(self, event):

        print('GrowingTextBrowser.resizeEvent', self._id, \
            'old', event.oldSize().width(), event.oldSize().height(), \
            'new', event.size().width(), event.size().height())
        self.print_document_size()
        return super(GrowingTextBrowser, self).resizeEvent(event)

####################################################################################################

def append_block(parent, vertical_layout, source_text):

    text_browser = GrowingTextBrowser(parent)
    text_browser.setPlainText(source_text)
    # vertical_layout.addWidget(text_browser)
    horizontal_layout = QtWidgets.QHBoxLayout()
    horizontal_layout.addWidget(text_browser, 0, QtCore.Qt.AlignTop)
    vertical_layout.addLayout(horizontal_layout)

def show_text_page(text_page):

    application = QtWidgets.QApplication(sys.argv)

    main_window = QtWidgets.QMainWindow()
    main_window.resize(1000, 800)
    main_window.setWindowTitle(args.filename)

    scroll_area = QtWidgets.QScrollArea(main_window)
    # scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
    scroll_area.setWidgetResizable(True)
    main_window.setCentralWidget(scroll_area)

    container_widget = QtWidgets.QWidget()
    vertical_layout = QtWidgets.QVBoxLayout(container_widget) # Set container_widget layout
    scroll_area.setWidget(container_widget)

    for block in mupdf_iter.TextBlockIterator(text_page):
        block_text = ''
        for line in mupdf_iter.TextLineIterator(block):
            line_text = ''
            for span in mupdf_iter.TextSpanIterator(line):
                span_text = ''
                for ch in mupdf_iter.TextCharIterator(span):
                    span_text += chr(ch.c)
                span_text = span_text.rstrip()
                if span_text: # Append span to line
                    line_text += span_text
                else: # Empty span then append a block
                    if block_text:
                        append_block(container_widget, vertical_layout, block_text)
                    block_text = ''
                    line_text = ''
            # Append line to block
            if block_text:
                block_text += ' '
            block_text += line_text
        if block_text:
            append_block(container_widget, vertical_layout, block_text)

    spacer_item = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
    vertical_layout.addItem(spacer_item)

    print('Show')
    #main_window.show()
    main_window.showMaximized()
    application.exec_()

####################################################################################################

argument_parser = argparse.ArgumentParser(description='Example.')

argument_parser.add_argument('filename', metavar='FILENAME',
                             help='PDF file')

argument_parser.add_argument('--page', dest='page_number',
                             type=int,
                             default=1,
                             help='Page number')

argument_parser.add_argument('--zoom', dest='zoom',
                             type=int,
                             default=100,
                             help='Zoom factor in %%')

argument_parser.add_argument('--rotation', dest='rotation',
                             type=int,
                             default=0,
                             help='Rotation')

args = argument_parser.parse_args()

####################################################################################################

# Create a context to hold the exception stack and various caches.
ctx = mupdf.new_context()

####################################################################################################

# Open the PDF, XPS or CBZ document.
doc = mupdf.open_document(ctx, args.filename.encode('utf-8'))

show_metadata(ctx, doc)

####################################################################################################

# Retrieve the number of pages (not used in this example).
page_count = mupdf.count_pages(doc)

# Load the page we want. Page numbering starts from zero.
page = mupdf.load_page(doc, args.page_number -1)

####################################################################################################

# Calculate a transform to use when rendering. This transform contains the scale and
# rotation. Convert zoom percentage to a scaling factor. Without scaling the resolution is 72 dpi.
transform = mupdf.Matrix()
mupdf.rotate(transform, args.rotation)
mupdf.pre_scale(transform, args.zoom / 100.0, args.zoom / 100.0)

# Take the page bounds and transform them by the same matrix that we will use to render the page.
bounds = mupdf.Rect()
mupdf.bound_page(doc, page, bounds)
mupdf.transform_rect(bounds, transform)

####################################################################################################

# A page consists of a series of objects (text, line art, images, gradients). These objects are
# passed to a device when the interpreter runs the page. There are several devices, used for
# different purposes:
#
#	draw device -- renders objects to a target pixmap.
#
#	text device -- extracts the text in reading order with styling
#	information. This text can be used to provide text search.
#
#	list device -- records the graphic objects in a list that can
#	be played back through another device. This is useful if you
#	need to run the same page through multiple devices, without
#	the overhead of parsing the page each time.

####################################################################################################

# Create a blank pixmap to hold the result of rendering. The pixmap bounds used here are the same as
# the transformed page bounds, so it will contain the entire page. The page coordinate space has the
# origin at the top left corner and the x axis extends to the right and the y axis extends down.
bbox = mupdf.IRect()
mupdf.round_rect(bbox, bounds)
width, height = bbox.x1 - bbox.x0, bbox.y1 - bbox.y0
np_array = np.zeros((height, width, 4), dtype=np.uint8)
# pixmap = mupdf.new_pixmap_with_bbox(ctx, mupdf.get_fz_device_rgb(), bbox)
pixmap = mupdf.new_pixmap_with_bbox_and_data(ctx, mupdf.device_rgb(ctx), bbox,
                                                 mupdf.np_array_uint8_ptr(np_array))
mupdf.clear_pixmap_with_value(ctx, pixmap, 0xff)

# Create a draw device with the pixmap as its target.
# Run the page with the transform.
device = mupdf.new_draw_device(ctx, pixmap)
mupdf.set_aa_level(ctx, 8)
mupdf.run_page(doc, page, device, transform, mupdf.NULL)
mupdf.free_device(device)

if True:
    show_pdf(np_array)

if True:
    # Save the pixmap to a file.
    mupdf.write_png(ctx, pixmap, 'out.png'.encode('utf-8'), 0)

####################################################################################################

text_sheet = mupdf.new_text_sheet(ctx)
text_page = mupdf.new_text_page(ctx)

device = mupdf.new_text_device(ctx, text_sheet, text_page)
mupdf.run_page(doc, page, device, transform, mupdf.NULL)
mupdf.free_device(device)

if True:
    # Dump text style and page.
    dump_text_style(text_sheet)
    dump_text_page_xml(text_page)

if True:
    dump_text_page(text_page)
    show_text_page(text_page)

if True:
    file_handler = mupdf.fopen('out.css'.encode('utf-8'), 'w+'.encode('ascii'))
    output_file = mupdf.new_output_with_file(ctx, file_handler)
    mupdf.print_text_sheet(ctx, output_file, text_sheet)
    mupdf.close_output(output_file)
    #? mupdf.fclose(file_handler)

    output_file = mupdf.fopen('out.txt'.encode('utf-8'), 'w+'.encode('ascii'))
    output_file = mupdf.new_output_with_file(ctx, file_handler)
    # mupdf.print_text_page(ctx, output_file, text_page)
    # mupdf.print_text_page_html(ctx, output_file, text_page)
    mupdf.print_text_page_xml(ctx, output_file, text_page)
    mupdf.close_output(output_file)
    #? mupdf.fclose(file_handler)

####################################################################################################

# Clean up.
mupdf.free_text_sheet(ctx, text_sheet)
mupdf.free_text_page(ctx, text_page)
mupdf.drop_pixmap(ctx, pixmap)
mupdf.free_page(doc, page)
mupdf.close_document(doc)
mupdf.free_context(ctx)
