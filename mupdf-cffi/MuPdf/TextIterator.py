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

import Babel.backend.MuPdf as _mupdf

####################################################################################################

def text_block_iterator(structured_text_page):

    block = structured_text_page.first_block
    while block != _mupdf.NULL:
        if block.type == _mupdf.FZ_STEXT_BLOCK_TEXT:
            yield block
        block = block.next

####################################################################################################

def text_line_iterator(block):

    line = block.u.t.first_line
    while line != _mupdf.NULL:
        yield line
        line = line.next

####################################################################################################

def text_char_iterator(line):

    char = line.first_char
    while char != _mupdf.NULL:
        yield char
        char = char.next
