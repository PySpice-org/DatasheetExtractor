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

import logging
import os

####################################################################################################

from DatasheetExtractor.backend.pdf.page import PdfPage

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class PinoutExtractor:

    ##############################################

    def __init__(self, page: PdfPage) -> None:
        self._page = page

    ##############################################

    def extract_pinout(self, axe: str = 'y') -> dict:
        ys = self._page.sort_xy(axe, ensure_direction=True, round_scale=10)
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
    def format_pinout(pins: dict) -> str:
        text = ''
        for key in sorted(pins.keys()):
            text += f' {key}: {pins[key]}' + os.linesep
        return text
