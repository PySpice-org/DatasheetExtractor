#! /usr/bin/env python3
# -*- Python -*-

####################################################################################################

import argparse

import numpy as np
from PIL import Image

import Babel.MuPdf as mupdf

####################################################################################################

def show_metadata(ctx, doc):

    for key in (
            'Title',
	    'Author',
	    'Subject',
	    'Keywords',
	    'Creator',
	    'Producer',
	    'CreationDate',
	    'ModDate',
    ):
        print('{}: {}'.format(key, mupdf.get_meta_info(ctx, doc, 'info:' + key, 1024)))

    # fz_buffer = mupdf.pdf_metadata(doc)
    # print(mupdf.decode_utf8(mupdf.buffer_data(fz_buffer)))
    # mupdf.drop_buffer(ctx, fz_buffer)

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

# Create a context to hold the exception stack and various caches
ctx = mupdf.new_context()
# ctx can be nullptr

# Register the default file types to handle
# fz_try(ctx)
mupdf.register_document_handlers(ctx)
# fz_catch(ctx)
#   "cannot register document handlers: %s\n", fz_caught_message(ctx)

mupdf.set_aa_level(ctx, 8) # number of bits of antialiasing (0 to 8)

####################################################################################################

# Open the PDF, XPS or CBZ document
# fz_try(ctx)
doc = mupdf.open_document(ctx, args.filename.encode('utf-8'))
# fz_catch(ctx)
#   "cannot open document: %s\n", fz_caught_message(ctx));

# fz_layout_document(ctx, doc, layout_w, layout_h, layout_em);

show_metadata(ctx, doc)

####################################################################################################

# Count the number of pages
# fz_try(ctx)
page_count = mupdf.count_pages(ctx, doc)
# fz_catch(ctx)
#   "cannot count number of pages: %s\n", fz_caught_message(ctx));
print('page_count: {}'.format(page_count))

# fz_load_outline(ctx, doc)

# fz_is_page_range(ctx, str(args.page_number))

# Load the page we want. Page numbering starts from zero.
page = mupdf.load_page(ctx, doc, args.page_number -1)

# Determine the size of a page at 72 dpi
mediabox = mupdf.Rect()
mupdf.bound_page(ctx, page, mediabox)
print(mupdf.str_rect(mediabox))

####################################################################################################
#
# Create display lists
#

page_list = mupdf.new_display_list(ctx, mupdf.NULL)
device = mupdf.new_list_device(ctx, page_list)
# if no_cache:
#     mupdf.enable_device_hints(ctx, device, mupdf.FZ_NO_CACHE)
mupdf.run_page_contents(ctx, page, device, mupdf.identity, mupdf.NULL)
mupdf.close_device(ctx, device)
mupdf.drop_device(ctx, device)

# mupdf.load_links(ctx, page)

####################################################################################################

def run_page(ctx, page_list, device,
             transform=mupdf.identity, # or ctm
             rect=mupdf.infinite_rect,
             cookie=mupdf.NULL,
):
    mupdf.run_display_list(ctx, page_list, device, transform, rect, cookie)
    # mupdf.run_display_list(ctx, annotations_list, dev, transform, rect, cookie)

####################################################################################################
#
# Extract text
#

structured_text_page = mupdf.new_stext_page(ctx, mediabox)
text_device = mupdf.new_stext_device(ctx, structured_text_page, mupdf.NULL)
run_page(ctx, page_list, text_device)
mupdf.close_device(ctx, text_device)
mupdf.drop_device(ctx, text_device)
print('Page has {} characters'.format(mupdf.stext_char_count(ctx, structured_text_page)))
print('Page mediabox {}'.format(mupdf.str_rect(structured_text_page.mediabox)))

block = structured_text_page.first_block
while block != mupdf.NULL:
    print('Block type:{} bbox:{}'.format(block.type, mupdf.str_rect_float(block.bbox)))
    if block.type == mupdf.FZ_STEXT_BLOCK_TEXT:
        line = block.u.t.first_line
        while line != mupdf.NULL:
            print('  Line wmode:{} dir:{} bbox:{}'.format(
                line.wmode,
                mupdf.str_point(line.dir),
                mupdf.str_rect_float(line.bbox),
            ))
            char = line.first_char
            while char != mupdf.NULL:
                print('    Char {} origin:{} bbox:{} size:{:.2f} font:{}'.format(
                    chr(char.c),
                    mupdf.str_point(char.origin),
                    mupdf.str_rect_float(char.bbox),
                    char.size,
                    mupdf.font_name(ctx, char.font),
                ))
                char = char.next
            line = line.next
    block = block.next

mupdf.drop_stext_page(ctx, structured_text_page)

structured_text_options = mupdf.StructuredTextOptions()
buffer_ = mupdf.new_buffer_from_page(ctx, page, structured_text_options)
text = mupdf.string_from_buffer(ctx, buffer_)
# print(mupdf.decode_utf8(text))
with open('out.txt', 'w') as fh:
    fh.write(mupdf.decode_utf8(text))
mupdf.drop_buffer(ctx, buffer_)

####################################################################################################

def pixmap_to_np_array(pixmap):

    samples = mupdf.pixmap_samples(ctx, pixmap)
    height = mupdf.pixmap_height(ctx, pixmap)
    width = mupdf.pixmap_width(ctx, pixmap)
    stride = mupdf.pixmap_stride(ctx, pixmap)
    number_of_samples = stride // width # = 3
    # number_of_samples = 3
    print('pixmap: {}x{}x{}'.format(height, width, number_of_samples))

    # Type = mupdf._ffi.getctype(mupdf._ffi.typeof(samples).item )
    # print(Type, mupdf._ffi.sizeof(Type))

    np_array = np.frombuffer(mupdf._ffi.buffer(samples, height*width*number_of_samples), dtype=np.uint8)
    np_array.shape = height, width, number_of_samples # np.reshape

    return np_array

# Save the pixmap to a file.
def save_image(np_array, path, mode='RGB'):
    image = Image.fromarray(np_array, mode=mode)
    image.save(path)

####################################################################################################
#
# Draw
#

# Get colorspace representing device specific rgb
color_space = mupdf.device_rgb(ctx)

# Compute a transformation matrix for the zoom and rotation desired.
# The default resolution without scaling is 72 dpi.
transform = mupdf.Matrix()
mupdf.scale(transform, args.zoom / 100.0, args.zoom / 100.0) # or resolution/72.
mupdf.pre_rotate(transform, args.rotation)

# bbox or bounds
ibbox = mupdf.IRect()
mupdf.round_rect(ibbox, mupdf.transform_rect(mediabox, transform))
print(mupdf.str_rect(ibbox))
bbox = mupdf.Rect()
mupdf.rect_from_irect(bbox, ibbox)
print(mupdf.str_rect(bbox))

# width, height = ibbox.x1 - ibbox.x0, ibbox.y1 - ibbox.y0
width, height = mupdf.rect_width_height(ibbox)
np_array = np.zeros((height, width, 4), dtype=np.uint8)

use_alpha = True
# pixmap = mupdf.new_pixmap_with_bbox(ctx, color_space, ibbox, mupdf.NULL, use_alpha)
pixmap = mupdf.new_pixmap_with_bbox_and_data(ctx, color_space, ibbox, mupdf.NULL, use_alpha,
                                              mupdf.np_array_uint8_ptr(np_array))
mupdf.clear_pixmap_with_value(ctx, pixmap, 255); # 0xff

image_device = mupdf.new_draw_device(ctx, mupdf.NULL, pixmap)
run_page(ctx, page_list, image_device, transform, bbox)
mupdf.close_device(ctx, image_device)
mupdf.drop_device(ctx, image_device)

# np_array = pixmap_to_np_array(pixmap)
save_image(np_array, 'out1.png', mode='RGBA')

mupdf.drop_pixmap(ctx, pixmap)

####################################################################################################

# Render page to an RGB pixmap
# fz_try(ctx)
pixmap = mupdf.new_pixmap_from_page(
    ctx, page,
    transform,
    color_space,
    0 # alphabits
)
# fz_catch(ctx)
#   "cannot render page: %s\n", fz_caught_message(ctx));

np_array = pixmap_to_np_array(pixmap)
save_image(np_array, 'out2.png', mode='RGB')

mupdf.drop_pixmap(ctx, pixmap)

####################################################################################################
#
# Clean up
#

mupdf.drop_display_list(ctx, page_list)
mupdf.drop_page(ctx, page)
mupdf.drop_document(ctx, doc)
mupdf.drop_context(ctx)
