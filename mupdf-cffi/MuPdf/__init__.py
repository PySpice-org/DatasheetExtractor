####################################################################################################
#
# Babel - An Electronic Document Management System
# Copyright (C) 2014 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

"""This module implements a Python bindings for the MuPdf library using the C Foreign Function
Interface for Python.

The difference to the C API are the followings:

* The "fz_" prefix is removed.

"""

####################################################################################################

import numpy as np

####################################################################################################

from _mupdf import ffi as _ffi
from _mupdf import lib as _lib

####################################################################################################
#
# Numpy interface
#

def np_array_ptr(array):
    return _ffi.cast('void *', array.__array_interface__['data'][0])

def np_array_uint8_ptr(array):
    if array.dtype == np.uint8:
        return _ffi.cast('unsigned char *', array.__array_interface__['data'][0])
    else:
        raise ValueError("Wrong Numpy array type")

####################################################################################################
#
# String Tools
#

def decode_utf8(ptr, max_length=None):
    if ptr == _ffi.NULL:
        return ''
    else:
        if max_length is not None:
            string = _ffi.string(ptr, max_length)
        else:
            string = _ffi.string(ptr)
        try:
            return string.decode('utf-8')
        except UnicodeDecodeError:
            return str(string)

####################################################################################################
#
# MuPdf API
#

###################################################
#
# Structures constructors
#

def Matrix():
    return _ffi.new('fz_matrix *')

def Rect():
    return _ffi.new('fz_rect *')

def IRect():
    return _ffi.new('fz_irect *')

def StructuredTextOptions(flags=0):
    stext_options = _ffi.new("fz_stext_options *")
    stext_options.flags = flags
    return stext_options


def rect_width_height(rect):
    return (rect.x1 - rect.x0,
            rect.y1 - rect.y0)

def str_point(point):
    return '[{0.x:.2f}, {0.y:.2f}]'.format(point)

def str_matrix(matrix):
    return '[{0.a:.2f}, {0.b:.2f}, {0.c:.2f}, {0.d:.2f}, {0.e:.2f}, {0.f:.2f}]'.format(matrix)

def str_rect(rect):
    return '[{0.x0}, {0.x1}]x[{0.y0}, {0.y1}]'.format(rect)

def str_rect_float(rect):
    return '[{0.x0:.2f}, {0.x1:.2f}]x[{0.y0:.2f}, {0.y1:.2f}]'.format(rect)

###################################################
#
# Constantes
#

# for convenience
NULL = _ffi.NULL # C NULL pointer

# Fixme:
FZ_STORE_UNLIMITED = _lib.FZ_STORE_UNLIMITED

FZ_NO_CACHE = _lib.FZ_NO_CACHE

FZ_STEXT_PRESERVE_LIGATURES = _lib.FZ_STEXT_PRESERVE_LIGATURES
FZ_STEXT_PRESERVE_WHITESPACE = _lib.FZ_STEXT_PRESERVE_WHITESPACE
FZ_STEXT_PRESERVE_IMAGES = _lib.FZ_STEXT_PRESERVE_IMAGES

FZ_STEXT_BLOCK_TEXT = _lib.FZ_STEXT_BLOCK_TEXT
FZ_STEXT_BLOCK_IMAGE = _lib.FZ_STEXT_BLOCK_IMAGE

###################################################
#
# Functions
#

# from fitz.h

# buffer
drop_buffer = _lib.fz_drop_buffer
# buffer_storage
string_from_buffer = _lib.fz_string_from_buffer

# colorspace
device_rgb = _lib.fz_device_rgb

# context
drop_context = _lib.fz_drop_context
# new_context
set_aa_level = _lib.fz_set_aa_level
caught_message = _lib.fz_caught_message

# device
drop_device = _lib.fz_drop_device
close_device = _lib.fz_close_device
enable_device_hints= _lib.fz_enable_device_hints
new_draw_device= _lib.fz_new_draw_device

# display-list
drop_display_list = _lib.fz_drop_display_list
new_display_list = _lib.fz_new_display_list
new_list_device = _lib.fz_new_list_device
run_display_list = _lib.fz_run_display_list

# document
drop_document = _lib.fz_drop_document
drop_page = _lib.fz_drop_page
bound_page = _lib.fz_bound_page
count_pages = _lib.fz_count_pages
load_links  = _lib.fz_load_links
# fz_lookup_metadata
open_document = _lib.open_document
register_document_handlers = _lib.fz_register_document_handlers
run_page = _lib.fz_run_page
run_page_contents  = _lib.fz_run_page_contents

# font
font_is_bold = _lib.fz_font_is_bold
font_is_italic = _lib.fz_font_is_italic
# font_name = _lib.fz_font_name

# geometry
identity  = _ffi.addressof(_lib.fz_identity)
infinite_rect  = _ffi.addressof(_lib.fz_infinite_rect)
concat = _lib.fz_concat
pre_rotate = _lib.fz_pre_rotate
pre_scale = _lib.fz_pre_scale
rect_from_irect = _lib.fz_rect_from_irect
round_rect = _lib.fz_round_rect
rotate = _lib.fz_rotate
scale = _lib.fz_scale
transform_rect = _lib.fz_transform_rect

# pixmap
drop_pixmap = _lib.fz_drop_pixmap
clear_pixmap_with_value  = _lib.fz_clear_pixmap_with_value
new_pixmap_with_bbox = _lib.fz_new_pixmap_with_bbox
new_pixmap_with_bbox_and_data = _lib.fz_new_pixmap_with_bbox_and_data
pixmap_height = _lib.fz_pixmap_height
pixmap_samples = _lib.fz_pixmap_samples
pixmap_stride = _lib.fz_pixmap_stride
pixmap_width = _lib.fz_pixmap_width
set_pixmap_resolution = _lib.fz_set_pixmap_resolution

# structured-text
drop_stext_page = _lib.fz_drop_stext_page
new_stext_page = _lib.fz_new_stext_page
new_stext_device = _lib.fz_new_stext_device
stext_char_at  = _lib.fz_stext_char_at
stext_char_count = _lib.fz_stext_char_count

# util
new_pixmap_from_page = _lib.fz_new_pixmap_from_page
new_pixmap_from_page_number = _lib.fz_new_pixmap_from_page_number
new_pixmap_from_page_contents = _lib.fz_new_pixmap_from_page_contents
new_stext_page_from_page = _lib.fz_new_stext_page_from_page
new_stext_page_from_page_number = _lib.fz_new_stext_page_from_page_number
new_buffer_from_page = _lib.fz_new_buffer_from_page
new_buffer_from_page_number = _lib.fz_new_buffer_from_page_number

# from pdf.h
load_page = _lib.fz_load_page

####################################################################################################
#
# Pythonic API
#
####################################################################################################

def version():
    return decode_utf8(_lib.MUPDF_VERSION)

####################################################################################################

def new_context(alloc=_ffi.NULL, locks=_ffi.NULL, max_store=_lib.FZ_STORE_UNLIMITED):
    ctx = _lib.fz_new_context(alloc, locks, max_store)
    if ctx == _ffi.NULL:
        raise NameError('cannot create mupdf context')
    else:
        return ctx

####################################################################################################

class Context:

    ##############################################

    def __init__(self, alloc=_ffi.NULL, locks=_ffi.NULL, max_store=_lib.FZ_STORE_UNLIMITED):

        self._context = _lib.fz_new_context(alloc, locks, max_store)

    ##############################################

    def __del__(self):

        _lib.fz_drop_context(self._context)

####################################################################################################

def font_name(ctx, font):
    return decode_utf8(_lib.fz_font_name(ctx, font))

####################################################################################################

def get_meta_info(ctx, document, key, size=1024):
    buffer_ = _ffi.new('char[]', size) # size in bytes
    key = key.encode('utf-8')
    # key_buffer = _ffi.new('char[]', key)
    # buffer_[0] = _ffi.addressof(key_buffer, 0)
    rc = _lib.fz_lookup_metadata(ctx, document, key, buffer_, size)
    if rc == -1: # key is not recognized or found
        # raise NameError('Meta info %s not found', key)
        return ''
    else:
        return decode_utf8(buffer_)

####################################################################################################
#
# API extensions
#

copy_irect = _lib.fz_copy_irect
copy_rect = _lib.fz_copy_rect
fclose = _lib.fz_fclose
fopen = _lib.fz_fopen

####################################################################################################
#
# Error Management
#

class MupdfError(NameError):
    pass

# @_ffi.callback("void(char *)")
# def throw_exit_callback(message):
#     raise MupdfError(decode_utf8(message))

# _lib.fz_set_throw_exit_callback(throw_exit_callback)
