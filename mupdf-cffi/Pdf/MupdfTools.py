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

# Fixme: remove useless code

####################################################################################################

import Babel.backend.MuPdf as mupdf
import Babel.backend.MuPdf.TextIterator as mupdf_iter

####################################################################################################

from .TextStyle import TextStyle
from Babel.backend.Math.Interval import IntervalInt2D

####################################################################################################

def indent_line(text, indent_level, indent_pattern='  '):

    # Fixme: not here, purpose ?

    return indent_pattern*indent_level + text + '\n'

####################################################################################################

def get_font_name(font):

    """ Return the name of a MuPDF font. """

    font_name = mupdf.decode_utf8(mupdf.get_font_name(font))
    i = font_name.find('+')
    if i:
        font_name = font_name[i+1:]

    return font_name

####################################################################################################

def format_bounding_box(obj):

    return "[%g %g %g %g]" % (obj.bbox.x0, obj.bbox.y0,
                              obj.bbox.x1, obj.bbox.y1)

####################################################################################################

def to_interval(bounding_box):

    """ Convert a MuPDF bounding box to an :obj:`Babel.Math.Interval.IntervalInt2D` object. """

    return IntervalInt2D((bounding_box.x0, bounding_box.x1),
                         (bounding_box.y0, bounding_box.y1))

####################################################################################################

def span_to_string(span):

    """ Return the unicode string corresponding to a MuPDF span. """

    span_text = ''
    for char in mupdf_iter.TextCharIterator(span):
        span_text += chr(char.c)
    span_text = span_text.rstrip()

    return span_text

####################################################################################################

def to_text_style(style):

    """ Convert a MuPDF style instance to a :obj:`.TextStyle` object. """

    font = style.font
    text_style = TextStyle(id=style.id,
                           font_family=get_font_name(font),
                           font_size=style.size,
                           is_bold=bool(mupdf.font_is_bold(font)),
                           is_italic=bool(mupdf.font_is_italic(font)),
                           )

    return text_style
