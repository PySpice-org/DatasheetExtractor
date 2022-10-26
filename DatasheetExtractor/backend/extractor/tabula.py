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

__all__ = ['TabulaExtractor']

####################################################################################################

import logging
from pathlib import Path

import tabula

# https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html
from pandas import DataFrame

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class TabulaExtractor:

    ##############################################

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    ##############################################

    def extract(
            self,
            page_number: int,
            guess: bool = True,
            lattice: bool = True,
            relative_area: list[int, int, int, int] = None,
            to_csv: bool = False,
    ) -> list[DataFrame]:
        kwargs = {}
        if relative_area:
            # top, left, bottom, right
            kwargs['area'] = [100*_ for _ in relative_area[:4]]
        # https://tabula-py.readthedocs.io/en/latest/tabula.html#tabula.io.read_pdf
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
        if to_csv:
            return [_.to_csv() for _ in _]
        else:
            return _
