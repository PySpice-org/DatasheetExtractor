####################################################################################################
#
# DatasheetExtractor - A Python library to extract data from datasheet
# Copyright (C) 2022 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
####################################################################################################

####################################################################################################

__all__ = ['PdfPage']

####################################################################################################

# from pathlib import Path
# from pprint import pprint
from typing import Iterator

from enum import Enum, auto
import logging
import io

# https://github.com/pymupdf/PyMuPDF
import fitz

import numpy as np

from IntervalArithmetic import IntervalInt2D

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Direction(Enum):
    horizontal = auto()
    vertical = auto()

####################################################################################################

class Line:

    ##############################################

    def __init__(self, x: int, y: int, bbox: list[int], direction: Direction, size: float, text: str, location: str) -> None:
        self.x = x
        self.y = y
        x_min, y_min, x_max, y_max = bbox
        self.bbox = IntervalInt2D((x_min, x_max), (y_min, y_max))
        self.size = size
        self.text = text
        self.direction = direction
        self.location = location
        self.siblings = []

    ##############################################

    @property
    def center(self) -> list[int]:
        return [int(_) for _ in self.bbox.center]

    @property
    def center_x(self) -> int:
        return self.center[0]

    @property
    def center_y(self) -> int:
        return self.center[1]

    @property
    def x_min(self) -> int:
        return self.bbox.x.inf

    @property
    def x_max(self) -> int:
        return self.bbox.x.sup

    @property
    def y_min(self) -> int:
        return self.bbox.y.inf

    @property
    def y_max(self) -> int:
        return self.bbox.y.sup

    @property
    def siblings_bbox(self):
        bbox = self.bbox.clone()
        for _ in self.siblings:
            bbox |= _.bbox
        return bbox

    @property
    def center_x_inclusive(self):
        if self.siblings:
            return self.siblings_bbox.center[0]
        else:
            return self.center_y

    @property
    def center_y_inclusive(self):
        if self.siblings:
            return self.siblings_bbox.center[1]
        else:
            return self.center_y

    ##############################################

    def __repr__(self) -> str:
        direction = 'H' if self.direction == Direction.horizontal else 'V'
        def format_position(position):
            return [int(_/10) for _ in position]
        x, y = format_position((self.x, self.y))
        center = format_position(self.center)
        size = self.size / 10
        return f'Line l={self.location} o=({x}, {y}) c={center} {direction} @{size} | {self.text}'

    ##############################################

    def link(self, line: 'Line') -> None:
        self.siblings.append(line)

####################################################################################################

class PdfPage:

    # API: https://pymupdf.readthedocs.io/en/latest/page.html
    # Appendix 1: Details on Text Extraction https://pymupdf.readthedocs.io/en/latest/app1.html

    ###! to transform float X.12... to int X1
    UNIT_SCALE = 10

    ##############################################

    @classmethod
    def to_scaled(cls, x: float) -> int:
        return int(x * cls.UNIT_SCALE)

    @classmethod
    def from_scaled(cls, x: int) -> float:
        return x / cls.UNIT_SCALE

    ##############################################

    def __init__(self, document: 'Document', fitz_page) -> None:
        self._document = document
        self._fitz_page = fitz_page
        self._data = fitz_page.get_text('dict')

        # page.get_links()
        # page.annots()

    ##############################################

    def __int__(self) -> int:
        return self._fitz_page.number

    # Fixme: -> page_number ?
    @property
    def number(self) -> int:
        number = self._fitz_page.number
        if self._document.FIRST_PAGE_ONE:
            number += 1
        return number

    ##############################################

    def __repr__(self) -> str:
        return f'Page {self.number}'

    ##############################################

    @property
    def width(self):
        return self.to_scaled(self._data['width'])

    @property
    def height(self):
        return self.to_scaled(self._data['height'])

    ##############################################

    def pixmap(self, dpi: int = 72, alpha=False) -> fitz.Pixmap:
        # Pixmap has the dimension of the page with width and height rounded to integers and a default resolution of 72 dpi.
        #   210 mm / 25.4 * 72 = 595.27 px
        # so at 72 dpi pixmap coordinate are equivalent to page coordinate / UNIT_SCALE
        # https://pymupdf.readthedocs.io/en/latest/page.html#Page.get_pixmap
        # https://pymupdf.readthedocs.io/en/latest/pixmap.html#pixmap
        pix = self._fitz_page.get_pixmap(
            # matrix=,
            dpi=dpi,
            # colorspace=,
            # clip=,
            alpha=alpha,   # whether to add an alpha channel for transparency
            annots=False,
        )
        # return pix.samples, pix.width, pix.height, pix.stride, pix.alpha
        return pix

    ##############################################

    def np_pixmap(self, dpi: int = 72, alpha=False) -> np.ndarray:
        pix = self.pixmap(dpi, alpha)
        array = np.frombuffer(pix.samples, dtype=np.uint8)
        array.shape = pix.height, pix.width, 3
        # from PIL import Image
        # stream = pix.pil_tobytes(format='PNG')
        # image = Image.open(io.BytesIO(stream))
        # array = np.array(image)
        return array

    ##############################################

    def to_png(self, path: str, **kwargs: dict) -> None:
        from PIL import Image
        # np_array = self.np_pixmap(**kwargs)
        # Fixme: ValueError: buffer is not large enough
        # image = Image.fromarray(np_array, mode='RGBA')
        pix = self.pixmap(**kwargs)
        stream = pix.pil_tobytes(format='PNG')
        image = Image.open(io.BytesIO(stream))
        image.save(path)

    ##############################################

    @property
    def lines(self) -> Iterator[Line]:
        # lines are sorted by y block
        # then by x
        # right justified blocks on header are placed at the end
        for b, block in enumerate(self._data['blocks']):
            if 'lines' in block:
                for l, line in enumerate(block['lines']):
                    match line['dir']:
                        case (1.0, 0.0):
                            direction = Direction.horizontal
                        case (0.0, -1.0):
                            direction = Direction.vertical
                    for s, span in enumerate(line['spans']):
                        # pprint(span)
                        x, y = [self.to_scaled(_) for _ in span['origin']]
                        bbox = [self.to_scaled(_) for _ in span['bbox']]
                        size = self.to_scaled(span['size'])
                        location = f'{b}/{l}/{s}'
                        yield Line(x, y, bbox, direction, size, span['text'], location)

    ##############################################

    def filter_lines(self, size: float = None) -> Iterator[Line]:
        size = self.to_scaled(size)
        for line in self.lines:
            if size is not None and line.size == size:
                yield line

    ##############################################

    def sort_xy(
            self,
            axe: str = 'x',
            use_center1: bool = False,
            use_center2: bool = False,
            ensure_direction: bool = False,
            round_scale: int = 10,
    ) -> dict:
        # Create an axe map
        axe_map = {}
        for line in self.lines:
            if ensure_direction:
                if axe == 'y' and line.direction != Direction.horizontal:
                    continue
                if axe == 'x' and line.direction != Direction.vertical:
                    continue
            if use_center1:
                x = line.center_y if axe == 'y' else line.center_x
            else:
                x = line.y if axe == 'y' else line.x
            x = int(x / round_scale)
            axe_map.setdefault(x, [])
            axe_map[x].append(line)
        # sort on second axe
        for line in axe_map.values():
            def func(_: Line) -> int:
                if use_center2:
                    return _.center_x if axe == 'y' else _.center_y
                else:
                    return _.x if axe == 'y' else _.y
            line.sort(key=func)
        return axe_map
