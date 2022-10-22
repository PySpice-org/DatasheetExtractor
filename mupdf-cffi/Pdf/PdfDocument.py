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

####################################################################################################

import logging
import numpy as np

import Babel.backend.MuPdf as mupdf
from Babel.backend.MuPdf import MupdfError

from ..Corpus.DocumentWords import DocumentWords
from ..Document.Document import Document
from ..Tools.AttributeDictionaryInterface import ReadOnlyAttributeDictionaryInterface
from ..Tools.Object import clone
from .PdfImageCache import PdfImageCache
from .TextPage import TextPage

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class PdfDocument(Document):

    """ This class represents a PDF Document. """

    _logger = _module_logger.getChild('PdfDocument')

    ##############################################

    def __init__(self, path):

        super().__init__(path)

        self._context = None
        self._c_document = None
        self._pages = {} # page cache

        path = str(self._path).encode('utf-8')

        # try:
        # Create a context to hold the exception stack and various caches
        self._context = mupdf.new_context()
        # Register the default file types to handle
        mupdf.register_document_handlers(self._context)
        self._c_document = mupdf.open_document(self._context, path)
        # except MupdfError as exception:
        #     raise exception
        if self._c_document == mupdf.NULL:
            message = mupdf.decode_utf8(mupdf.caught_message(self._context))
            self._logger.error(message)
            raise MupdfError(message)
        self._metadata = MetaData(self)
        self._number_of_pages = mupdf.count_pages(self._context, self._c_document)
        self._document_words = None
        self._image_cache = None

    ##############################################

    def __del__(self):

        # Fixme: manage properly
        for page in self._pages.values():
            page._free() # require context
        if self._c_document is not None:
            mupdf.drop_document(self._context, self._c_document)
        if self._context is not None:
            mupdf.drop_context(self._context)

    ##############################################

    @classmethod
    def check_magic_number(cls, path):

        # %PDF-1.4^M...
        with open(str(path), 'rb') as fh:
            data = fh.read(32)
        return data[:5].decode('ascii') == '%PDF-'

    ##############################################

    @property
    def metadata(self):
        return self._metadata

    @property
    def number_of_pages(self):
        return self._number_of_pages

    ##############################################

    def _page(self, index):

        if not index in self._pages:
            page = Page(self, index)
            self._pages[index] = page
            return page
        else:
            return self._pages[index]

    ##############################################

    @property
    def first_page(self):
        return self._page(0)

    ##############################################

    def __getitem__(self, index):

        if isinstance(index, slice):
            return [self._page(i) for i in range(index.start, index.stop, index.step or 1)]
        else:
            return self._page(index)

    ##############################################

    def __iter__(self):

        for i in range(self._number_of_pages):
            yield self._page(i)

    ##############################################

    def iter_until(self, last_page=None):

        if last_page is None:
            last_page = self.number_of_pages -1

        for i in range(last_page +1):
            yield self._page(i)

    ##############################################

    @property
    def words(self):

        """ Return a :obj:`.DocumentWords` instance. """

        if self._document_words is None:
            self._document_words = self.collect_document_words()

        return self._document_words

    ##############################################

    def collect_document_words(self, last_page=None):

        document_words = DocumentWords()
        for page in self.iter_until(last_page):
            text_page = page.text
            tokenised_text = text_page.blocks.tokenised_text
            for token in tokenised_text.word_iterator():
                document_words.add(str(token).lower())
        document_words.sort()

        return document_words

    ##############################################

    def text(self, last_page=None):

        text = ''
        for page in self.iter_until(last_page):
            text += page.text_direct + '\n'

        return text

    ##############################################

    @property
    def image_cache(self):
        if self._image_cache is None:
            self._image_cache = PdfImageCache(self)
        return self._image_cache

####################################################################################################

class MetaData(ReadOnlyAttributeDictionaryInterface):

    """ This class gives access to the PDF metadata.

    Public Attributes:

      :attr:`Title`

      :attr:`Subject`

      :attr:`Author`

      :attr:`Creator`

      :attr:`Producer`

      :attr:`CreationDate`

      :attr:`ModDate`

    """

    ##############################################

    def __init__(self, document):

        super(MetaData, self).__init__()

        context = document._context
        c_document = document._c_document

        for key in (
                'Title',
                'Subject',
                'Author',
                'Creator',
                'Producer',
                'CreationDate',
                'ModDate',
        ):
            # Fixme: buffer size
            string = mupdf.get_meta_info(context, c_document, 'info:' + key, size=1024)
            self._dictionary[key] = string

        # fz_buffer = mupdf.pdf_metadata(c_document)
        # string = mupdf.decode_utf8(mupdf.buffer_data(fz_buffer))
        string = ''
        self._dictionary['metadata'] = string
        # mupdf.drop_buffer(document._context, fz_buffer)

####################################################################################################

class Page:

    """ This class represents a PDF Page. Its contents could be rastered to an image or extracted as
    a text representation.
    """

    ##############################################

    def __init__(self, document, page_number): # or page_index

        self._document = document
        self._context = self._document._context
        self._c_document = self._document._c_document
        self._page_number = page_number
        self._c_page = mupdf.load_page(self._context, self._c_document, page_number)
        self._text_page = None

    ##############################################

    @property
    def page_number(self):
        return self._page_number

    ##############################################

    def _free(self):

        if self._text_page is not None:
            self._text_page._free()
        mupdf.drop_page(self._context, self._c_page)

    ##############################################

    def __del__(self):

        pass

    ##############################################

    def _bounding_box(self):

        # Determine the size of the page at 72 dpi.
        mediabox = mupdf.Rect()
        mupdf.bound_page(self._context, self._c_page, mediabox)
        # 'mediabox {}'.format(mupdf.str_rect(mediabox)))

        return mediabox

    ##############################################

    def _make_display_list(self, no_cache=False):

        # Fixme: use it

        self._page_list = mupdf.new_display_list(self._context, mupdf.NULL)
        device = mupdf.new_list_device(self._context, page_list)
        if no_cache:
            mupdf.enable_device_hints(self._context, device, mupdf.FZ_NO_CACHE)
        mupdf.run_page_contents(self._context, page, device, mupdf.identity, mupdf.NULL)
        mupdf.close_device(self._context, device)
        mupdf.drop_device(self._context, device)

    ##############################################

    def _make_transform(self, scale=1, rotation=0):

        transform = mupdf.Matrix()
        # mupdf.rotate(transform, rotation)
        # mupdf.pre_scale(transform, scale, scale)
        mupdf.scale(transform, scale, scale)
        mupdf.pre_rotate(transform, rotation)

        return transform

    ##############################################

    def _transform_bounding_box(self,
                                rotation=0,
                                resolution=72,
                                width=0, height=0, fit=False):

        bounds = self._bounding_box()
        scale = resolution / 72.
        transform = mupdf.Matrix()
        mupdf.pre_scale(mupdf.rotate(transform, rotation), scale, scale)
        tmp_bounds = mupdf.Rect()
        mupdf.copy_rect(tmp_bounds, bounds)
        ibounds = mupdf.IRect()
        mupdf.round_rect(ibounds, mupdf.transform_rect(tmp_bounds, transform))

        # If a resolution is specified, check to see whether width/height are exceeded if not, unset them.
        if resolution != 72:
            actual_width = ibounds.x1 - ibounds.x0
            actual_height = ibounds.y1 - ibounds.y0
            if width and actual_width <= width:
                width = 0
            if height and actual_height <= height:
                height = 0

        # Now width or height will be 0 unless they need to be enforced.
        if width or height:
            scale_x = width  / (tmp_bounds.x1 - tmp_bounds.x0)
            scale_y = height / (tmp_bounds.y1 - tmp_bounds.y0)
            if fit: # ignore aspect
                if not scale_x:
                    scale_x = 1.0 # keep computed width
                elif not scale_y:
                    scale_y = 1.0 # keep computed height
            else:
                if not scale_x:
                    scale_x = scale_y
                elif not scale_y:
                    scale_y = scale_x
                else:
                    # take the smallest scale
                    if scale_x > scale_y:
                        scale_x = scale_y
                    else:
                        scale_y = scale_x
            scale_mat = mupdf.Matrix()
            mupdf.scale(scale_mat, scale_x, scale_y)
            mupdf.concat(transform, transform, scale_mat)
            mupdf.copy_rect(tmp_bounds, bounds)
            mupdf.transform_rect(tmp_bounds, transform)

        mupdf.round_rect(ibounds, tmp_bounds)

        return transform, ibounds

    ##############################################

    def to_pixmap(self,
                  rotation=0,
                  resolution=72,
                  width=None, height=None, fit=False,
                  antialiasing_level=8,
                  ):

        transform, bounding_box = self._transform_bounding_box(rotation,
                                                               resolution,
                                                               width, height, fit)

        width, height = mupdf.rect_width_height(bounding_box)
        np_array = np.zeros((height, width, 4), dtype=np.uint8)
        color_space = mupdf.device_rgb(self._context)
        use_alpha = True
        pixmap = mupdf.new_pixmap_with_bbox_and_data(self._context,
                                                     color_space,
                                                     bounding_box,
                                                     mupdf.NULL,
                                                     use_alpha,
                                                     mupdf.np_array_uint8_ptr(np_array))
        mupdf.clear_pixmap_with_value(self._context, pixmap, 255) # 0xff

        device = mupdf.new_draw_device(self._context, mupdf.NULL, pixmap)
        mupdf.set_aa_level(self._context, antialiasing_level)
        mupdf.run_page(self._context, self._c_page, device, transform, mupdf.NULL)
        mupdf.close_device(self._context, device)
        mupdf.drop_device(self._context, device)
        mupdf.drop_pixmap(self._context, pixmap)

        return np_array

    ##############################################

    def to_png(self, path, **kwargs):

        np_array = self.to_pixmap(**kwargs)

        from PIL import Image
        image = Image.fromarray(np_array, mode='RGBA')
        image.save(path)

    ##############################################

    def _to_text(self, scale=1, rotation=0):

        """ Return a :obj:`.TextPage` instance. """

        mediabox = self._bounding_box()
        transform = self._make_transform(scale, rotation)
        structured_text_options = mupdf.StructuredTextOptions()

        structured_text_page = mupdf.new_stext_page(self._context, mediabox)
        device = mupdf.new_stext_device(self._context, structured_text_page, structured_text_options)
        mupdf.run_page(self._context, self._c_page, device, transform, mupdf.NULL)
        # run_page(self._context, page_list, device)
        mupdf.close_device(self._context, device)
        mupdf.drop_device(self._context, device)

        # structured_text_page_ = mupdf.new_stext_page_from_page(self._context, self._c_page, structured_text_options)

        return TextPage(self, structured_text_page)

    ##############################################

    @property
    def text_direct(self):

        # Fixme: versus text

        structured_text_options = mupdf.StructuredTextOptions()
        c_buffer = mupdf.new_buffer_from_page(self._context, self._c_page, structured_text_options)
        py_buffer = mupdf.string_from_buffer(self._context, c_buffer)
        mupdf.drop_buffer(self._context, c_buffer)

        return mupdf.decode_utf8(py_buffer)

    ##############################################

    @property
    def text(self):

        if self._text_page is None:
            self._text_page = self._to_text()
        return self._text_page
