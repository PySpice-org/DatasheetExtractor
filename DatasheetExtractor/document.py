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

__all__ = ['Document']

####################################################################################################

from pathlib import Path
# from pprint import pprint
# from typing import Iterator
from urllib.parse import urlparse

import logging

import requests

# https://github.com/pymupdf/PyMuPDF
import fitz

####################################################################################################

from .page import Page

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Document:

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
            self._logger.info(f"Open {self.path}")
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
        return Page(self, page_number, fitz_page)

    __getitem__ = _load_page
