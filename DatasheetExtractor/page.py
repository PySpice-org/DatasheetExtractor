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

__all__ = ['Page']

####################################################################################################

# from pathlib import Path
# from pprint import pprint
from typing import Iterator

from enum import Enum, auto
import logging
import os

# https://github.com/pymupdf/PyMuPDF
# import fitz

from IntervalArithmetic import IntervalInt2D

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

UNIT_SCALE = 10

####################################################################################################

class Direction(Enum):
    horizontal = auto()
    vertical = auto()

####################################################################################################

class Line:

    ##############################################

    @classmethod
    def to_unit(cls, x: int) -> int:
        return x * UNIT_SCALE

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

class Page:

    ##############################################

    def __init__(self, number: int, data: dict) -> None:
        self._number = number
        self._data = data

    ##############################################

    @property
    def number(self):
        return self._number

    ##############################################

    def __repr__(self) -> str:
        return f'Page {self._number}'

    ##############################################

    @property
    def width(self):
        return self._data['width'] * UNIT_SCALE

    @property
    def height(self):
        return self._data['height'] * UNIT_SCALE

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
                        x, y = [int(_*UNIT_SCALE) for _ in span['origin']]
                        bbox = [int(_*UNIT_SCALE) for _ in span['bbox']]
                        size = int(span['size']*UNIT_SCALE)
                        location = f'{b}/{l}/{s}'
                        yield Line(x, y, bbox, direction, size, span['text'], location)

    ##############################################

    def filter_lines(self, size=None) -> Iterator[Line]:
        size *= UNIT_SCALE
        for line in self.lines:
            if size is not None and line.size == size:
                yield line

    ##############################################

    def _sort_xy(self, axe: str = 'x', use_center1=False, use_center2=False, ensure_direction=False, round_scale=10) -> dict:
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
            #! alist = axe_map.setdefault(x, [])
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

    ##############################################

    def extract_pinout(self, axe: str = 'y') -> dict:
        ys = self._sort_xy(axe, ensure_direction=True, round_scale=10)
        # pprint(ys)

        pins = {}
        for y in ys.values():
            if len(y) == 4:
                parts = [_.text for _ in y]
                int_count = 0
                for i, value in enumerate(parts):
                    try:
                        parts[i] = int(value)
                        int_count += 1
                    except ValueError:
                        pass
                if int_count == 2:
                    pin_l, l, r, pin_r = parts
                    pins[l] = pin_l
                    pins[r] = pin_r
        return pins

    ##############################################

    def extract_pinout_quad(self) -> dict:
        h_pins = self.extract_pinout(axe='y')
        v_pins = self.extract_pinout(axe='x')
        if v_pins and len(h_pins) != len(v_pins):
            raise NameError("H vs V number of pins mismatch")
        h_pins.update(v_pins)
        return h_pins

    ##############################################

    @staticmethod
    def format_pinout(pins) -> str:
        text = ''
        for key in sorted(pins.keys()):
            text += f' {key}: {pins[key]}' + os.linesep
        return text
