####################################################################################################

#from io import StringIO, BytesIO
from pprint import pprint

from lxml import etree

####################################################################################################

class StextExtractor:

    ##############################################

    def __init__(self, file_path: str) -> None:
        self._tree = etree.parse(file_path)

    ##############################################

    def extract_page_lines(self, page: int):
        # <page id="page14" width="612" height="792">
        pages = self._tree.xpath('page')
        page = pages[page -1]
        # print(page.items())
        # print(etree.tostring(page, pretty_print=True, encoding='unicode'))
        # lines = page.xpath('line')
        xml_lines = page.findall('.//line')
        lines = []
        for line in xml_lines:
            text = ''.join([_.attrib['c'] for _ in line.findall('.//char')])
            x, y = [int(float(_)*10) for _ in line.attrib['bbox'].split(' ')][:2]
            lines.append(dict(x=x, y=y, t=text))
        return lines

    ##############################################

    def extract_pinout(self, page: int):
        lines = self.extract_page_lines(page)

        ys = {}
        for line in lines:   # sorted(lines, key=lambda _: _['y']):
            y = line['y']
            alist = ys.setdefault(y, [])
            ys[y].append(line)
        for line in ys.values():
            line.sort(key=lambda _: _['x'])
        # pprint(ys)
        
        pins = {}
        for y in ys.values():
            if len(y) == 4:
                parts = [_['t'] for _ in y]
                for i, value in enumerate(parts):
                    try:
                        parts[i] = int(value)
                    except ValueError:
                        pass
                pin_l, l, r, pin_r = parts
                pins[l] = pin_l
                pins[r] = pin_r
        # pprint(pins)
        for key in sorted(pins.keys()):
            print(f' {key}: {pins[key]}')

    ##############################################

    def extract_pinout_quad(self, page: int, number_of_pins: int):
        lines = self.extract_page_lines(page)
        # lines.sort(lines, key=lambda _: _['y'])
        # pprint(lines)

        ys = {}
        for line in lines:   
            y = line['y']
            alist = ys.setdefault(y, [])
            ys[y].append(line)
        for line in ys.values():
            line.sort(key=lambda _: _['x'])

        for y in sorted(ys):
            _ = ys[y]
            print(y, len(_), _)

        pins = {}
        
        for y in ys.values():
            if len(y) == 4:
                parts = [_['t'] for _ in y]
                for i, value in enumerate(parts):
                    try:
                        parts[i] = int(value)
                    except ValueError:
                        pass
                pin_l, l, r, pin_r = parts
                pins[l] = pin_l
                pins[r] = pin_r

        for y in ys.values():
            if len(y) == number_of_pins/4:
                print(y)

        # pprint(pins)
        for key in sorted(pins.keys()):
            print(f' {key}: {pins[key]}')

####################################################################################################

file_path = 'AVR128DA28-32-48-64-Data-Sheet-40002183C.stxt'
extractor = StextExtractor(file_path)
# extractor.extract_pinout(page=14)
# lines = extractor.extract_page_lines(page=15)
# pprint(lines)
extractor.extract_pinout_quad(page=15, number_of_pins=32)

####################################################################################################
####################################################################################################

# lines = [
#     {'t': '2. ', 'x': 368, 'y': 874},
#     {'t': 'Pinout', 'x': 793, 'y': 874},
#     {'t': '2.1 ', 'x': 368, 'y': 1291},
#     {'t': '28-Pin SPDIP, SSOP and SOIC', 'x': 793, 'y': 1291},
#     {'t': '1', 'x': 2536, 'y': 1586},
#     {'t': '2', 'x': 2536, 'y': 1756},
#     {'t': '3', 'x': 2536, 'y': 1927},
#     {'t': '4', 'x': 2536, 'y': 2097},
#     {'t': '5', 'x': 2536, 'y': 2267},
#     {'t': '6', 'x': 2536, 'y': 2437},
#     {'t': '7', 'x': 2536, 'y': 2607},
#     {'t': '13', 'x': 2510, 'y': 3628},
#     {'t': '11', 'x': 2510, 'y': 3287},
#     {'t': '12', 'x': 2510, 'y': 3458},
#     {'t': '14', 'x': 2510, 'y': 3798},
#     {'t': '8', 'x': 2536, 'y': 2777},
#     {'t': '9', 'x': 2536, 'y': 2947},
#     {'t': '10', 'x': 2510, 'y': 3118},
#     {'t': '15', 'x': 3190, 'y': 3798},
#     {'t': '20', 'x': 3190, 'y': 2947},
#     {'t': '19', 'x': 3190, 'y': 3118},
#     {'t': '18', 'x': 3190, 'y': 3287},
#     {'t': '17', 'x': 3190, 'y': 3458},
#     {'t': '16', 'x': 3190, 'y': 3628},
#     {'t': '21', 'x': 3190, 'y': 2777},
#     {'t': '26', 'x': 3190, 'y': 1927},
#     {'t': '25', 'x': 3190, 'y': 2097},
#     {'t': '24', 'x': 3190, 'y': 2267},
#     {'t': '23', 'x': 3190, 'y': 2437},
#     {'t': '22', 'x': 3190, 'y': 2607},
#     {'t': '28', 'x': 3190, 'y': 1586},
#     {'t': '27', 'x': 3190, 'y': 1756},
#     {'t': 'VDD', 'x': 3527, 'y': 2947},
#     {'t': 'GND', 'x': 3527, 'y': 2777},
#     {'t': 'PA0 (EXTCLK)', 'x': 3527, 'y': 2607},
#     {'t': 'PA7', 'x': 2098, 'y': 1586},
#     {'t': 'PA2', 'x': 3527, 'y': 2267},
#     {'t': 'PA3', 'x': 3527, 'y': 2097},
#     {'t': 'PD4', 'x': 2093, 'y': 3118},
#     {'t': 'PD2', 'x': 2093, 'y': 2777},
#     {'t': 'PD3', 'x': 2093, 'y': 2947},
#     {'t': 'PD1', 'x': 2093, 'y': 2607},
#     {'t': 'PA4', 'x': 3527, 'y': 1927},
#     {'t': 'UPDI', 'x': 3527, 'y': 3118},
#     {'t': 'PF6 (RESET)', 'x': 3527, 'y': 3287},
#     {'t': 'PA1', 'x': 3527, 'y': 2437},
#     {'t': 'PF1 (XTAL32K2)', 'x': 3527, 'y': 3458},
#     {'t': 'PF0 (XTAL32K1)', 'x': 3527, 'y': 3628},
#     {'t': 'PC0', 'x': 2095, 'y': 1756},
#     {'t': 'PC1', 'x': 2093, 'y': 1927},
#     {'t': 'PC3', 'x': 2093, 'y': 2267},
#     {'t': 'PC2', 'x': 2093, 'y': 2097},
#     {'t': 'PD5', 'x': 2093, 'y': 3287},
#     {'t': 'GND', 'x': 3527, 'y': 3798},
#     {'t': 'PD7', 'x': 2093, 'y': 3628},
#     {'t': 'PA5', 'x': 3527, 'y': 1756},
#     {'t': 'PA6', 'x': 3527, 'y': 1586},
#     {'t': 'PD6', 'x': 2093, 'y': 3458},
#     {'t': 'AVDD', 'x': 2013, 'y': 3798},
#     {'t': 'PD0', 'x': 2093, 'y': 2437},
#     {'t': 'Power', 'x': 1397, 'y': 4210},
#     {'t': 'Power Supply', 'x': 1573, 'y': 4422},
#     {'t': 'Ground', 'x': 1575, 'y': 4662},
#     {'t': ' ', 'x': 1577, 'y': 4902},
#     {'t': 'Pin on AVDD Power Domain', 'x': 1573, 'y': 5143},
#     {'t': 'Functionality', 'x': 3083, 'y': 4210},
#     {'t': 'Programming/Debug', 'x': 3260, 'y': 4420},
#     {'t': 'Clock/Crystal', 'x': 3262, 'y': 4662},
#     {'t': 'Analog Function', 'x': 3267, 'y': 5142},
#     {'t': 'Digital Function Only', 'x': 3260, 'y': 4902},
#     {'t': 'Pin on VDD Power Domain', 'x': 1573, 'y': 4902},
#     {'t': 'Note: For the AVR® DA Family, the VDD and AVDD are internally connected (no separate power domains). ', 'x': 538, 'y': 5440},
#     {'t': ' AVR128DA28/32/48/64', 'x': 3731, 'y': 211},
#     {'t': 'Pinout', 'x': 5126, 'y': 419},
#     {'t': '© 2021 Microchip Technology Inc.', 'x': 765, 'y': 7598},
#     {'t': 'and its subsidiaries', 'x': 765, 'y': 7725},
#     {'t': ' Complete Datasheet', 'x': 2828, 'y': 7579},
#     {'t': 'DS40002183C-page 14', 'x': 4658, 'y': 7585},
# ]
