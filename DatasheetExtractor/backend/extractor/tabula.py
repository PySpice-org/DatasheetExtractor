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

"""This modules implements the Tabula extractor.

Tabula source code is hosted on this `repository <https://github.com/tabulapdf/tabula-java>`_

The guess algorithm search line intersections from the PDF.

The lattice mode use an algorithm from <Anssi Nurminen's master's
thesis`http://dspace.cc.tut.fi/dpub/bitstream/handle/123456789/21520/Nurminen.pdf?sequence=3`>_.  It
find cells by image processing.

"""

####################################################################################################

__all__ = ['TabulaExtractor']

####################################################################################################

import logging
from datetime import datetime
from pathlib import Path

import tabula

# https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html
from pandas import DataFrame

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class TabulaExtractor:

    _logger = _module_logger.getChild('TabulaExtractor')

    JAVA_URL = 'https://github.com/tabulapdf/tabula-java'
    PYTHON_URL = 'https://github.com/chezou/tabula-py'
    LICENSE = 'MIT'
    JAVA_LICENSES_URL = 'https://github.com/tabulapdf/tabula-java/blob/master/LICENSE'
    PYTHON_LICENSES_URL = 'https://github.com/chezou/tabula-py/blob/master/LICENSE'

    ##############################################

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    ##############################################

    def extract(
            self,
            page_number: int,
            guess: bool = True,
            relative_area: list[float, float, float, float] = None,
            scaled_by_100: bool = True,
            lattice: bool = True,
            to_csv: bool = False,
    ) -> list[DataFrame]:
        if page_number < 1:
            raise ValueError("page must be > 1")
        kwargs = {}
        if relative_area:
            # top, left, bottom, right
            area = relative_area[:4]
            if not scaled_by_100:
                area = [100*_ for _ in area]
            kwargs['area'] = area
        # https://tabula-py.readthedocs.io/en/latest/tabula.html#tabula.io.read_pdf
        self._logger.info('Start Tabula.java process...')
        start_time = datetime.now()
        _ = tabula.read_pdf(
            input_path=str(self._path),
            output_format='dataframe',   # json
            encoding='utf-8',
            # java_options='',
            # pandas_options='',
            multiple_tables=True,
            # user_agent
            # use_raw_url
            pages=int(page_number),
            guess=guess,
            relative_area=True,
            lattice=lattice,
            stream=not lattice,
            # password
            # silent
            # columns
            # format
            # batch
            # output_path
            # options
            **kwargs,
        )
        job_duration = datetime.now() - start_time
        self._logger.info(f'Tabula process done {job_duration}')
        if to_csv:
            return [_.to_csv() for _ in _]
        else:
            return _
