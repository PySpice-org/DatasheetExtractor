####################################################################################################

__all__ = ['DatasheetExtractor']

####################################################################################################

import logging
# logging.basicConfig(level=logging.NOTSET)
logging.root.setLevel(logging.NOTSET)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

handler = logging.StreamHandler()
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

logger.info("Start ...")

####################################################################################################

from pathlib import Path
from pprint import pprint
from typing import Iterator
from urllib.parse import urlparse

from enum import Enum, auto
import logging
import os
import subprocess
import tempfile

import requests

from lxml import etree

# https://github.com/pymupdf/PyMuPDF
import fitz

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
            alist = axe_map.setdefault(x, [])
            axe_map[x].append(line)
        # sort on second axe
        for line in axe_map.values():
            if use_center2:
                func = lambda _: _.center_x if axe == 'y' else _.center_y
            else:
                func = lambda _: _.x if axe == 'y' else _.y
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

    def format_pinout(pins) -> str:
        text = ''
        for key in sorted(pins.keys()):
            text += f' {key}: {pins[key]}' + os.linesep
        return text
        
####################################################################################################

class DatasheetExtractor:

    _logger = _module_logger.getChild('DatasheetExtractor')

    ##############################################

    def __init__(self, url: str, cache_path: str or Path = '.') -> None:
        self._url = str(url)
        self._cache_path = Path(cache_path)
        self._path = None
        self._doc = None

    ##############################################

    @property
    def url(self) -> str:
        return self._url

    ##############################################

    @property
    def path(self) -> str:
        if self._path is None:
            url_path = urlparse(self._url).path
            index = url_path.rfind('/')
            if index != -1 and index != (len(url_path) -1):
                filename = url_path[index+1:]
            else:
                raise NameError(f"Bad url {filename}")
            self._path = Path(self._cache_path).joinpath(filename)
        return self._path

    ##############################################

    def download(self) -> None:
        # https://requests.readthedocs.io/en/latest/user/quickstart/#make-a-request
        req = requests.get(self._url)
        if req.status_code != requests.codes.ok:
            raise NameError(f"Download failed for {self._url}")
        with open(self.path, 'wb') as fh:
            fh.write(req.content)
        self._logger.info(f"Downloaded {self._url}")

    ##############################################

    def _load(self) -> None:
        if self._doc is None:
            self._doc = fitz.open(self.path)
            self._get_metadata()
        return self._doc

    ##############################################

    def _get_metadata(self) -> None:
        doc = self._load()
        self._title = doc.metadata['title']
        self._author = doc.metadata['author']
        self._creator = doc.metadata['creator']
        self._creation_date = doc.metadata['creationDate']
        self._modification_date = doc.metadata['modDate']
        self._keywords = doc.metadata['keywords']
        self._subject = doc.metadata['subject']

    ##############################################

    def _load_page(self, page_number: int) -> Page:
        doc = self._load()
        fitz_page = doc[page_number -1]
        text = fitz_page.get_text('json')
        # print(text)
        data = fitz_page.get_text('dict')
        page = Page(number=page_number, data=data)
        return page

    __getitem__ = _load_page

    ##############################################

###    def _convert(self) -> None:
###        with tempfile.TemporaryDirectory() as dirname:
###            stext_path = Path(dirname).joinpath(self.path.name + '.stext')
###            mutool = '/usr/bin/mutool'
###            subprocess.check_call(
###                (
###                    mutool,
###                    'convert',
###                    '-F' , 'stext',
###                    '-o', str(stext_path),
###                    str(self.path),
###                ),
###            )
###            self._parse(stext_path)
###                
###    ##############################################
###
###    def _parse(self, stext_path: Path) -> None:
###        tree = etree.parse(str(stext_path))
###        # <document>
###        #   <page id="page1" width="612" height="792">
###        #     <block bbox="284.37806 101.32924 541.37368 128.14174">
###        #       <line bbox="284.37806 101.32924 541.37368 128.14174" wmode="0" dir="1 0">
###        #         <font name="Arial-BoldMT" size="24">
###        #           <char quad="284.37806 101.32924 291.04603 101.32924 284.37806 128.14174 291.04603 128.14174" x="284.37806" y="123.0558" color="#000000" c=" "/>
###        for page in tree.findall('page'):
###            self._handle_page(page)
###
###    ##############################################
###
###    def _handle_page(self, xml_page: etree.Element) -> None:
###        page_number = int(xml_page.attrib['id'][4:])
###        width = int(xml_page.attrib['width'])
###        height = int(xml_page.attrib['height'])
###        page = Page(number=page_number, height=height, width=width)
###
###        for xml_line in xml_page.findall('.//line'):
###            font_min = 10**9
###            font_max = 0
###            text = ''
###            x, y = [int(float(_)*10) for _ in xml_line.attrib['bbox'].split(' ')][:2]
###            for font in xml_line.findall('.//font'):
###                font_size = float(font.attrib['size'])
###                font_min = min(font_min, font_size)
###                font_max = max(font_max, font_size)
###                text += ''.join([_.attrib['c'] for _ in xml_line.findall('.//char')])
###            line = Line(x, y, [font_min, font_max], text)
