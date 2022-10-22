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

__all__ = ['PdfDocument']

####################################################################################################

from pathlib import Path
from typing import Iterator, Optional
from urllib.parse import urlparse

import logging

import requests

# https://github.com/pymupdf/PyMuPDF
import fitz

####################################################################################################

from .page import PdfPage
from .PdfImageCache import PdfImageCache
# from DatasheetExtractor.commmon.AttributeDictionaryInterface import ReadOnlyAttributeDictionaryInterface

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class PdfDocument:

    _logger = _module_logger.getChild('DatasheetExtractor')

    ##############################################

    @classmethod
    def check_magic_number(cls, path: str) -> bool:
        # %PDF-1.4^M...
        with open(str(path), 'rb') as fh:
            data = fh.read(32)
        return data[:5].decode('ascii') == '%PDF-'

    ##############################################

    def __init__(self, url: str, cache_path: str or Path = '.') -> None:
        url = str(url)
        parsed_url = urlparse(url)
        # Fixme: cls
        self._cache_path = Path(cache_path)
        self._doc = None
        self._pages = []
        self._image_cache = None
        if parsed_url.scheme:
            self._url = url
            self._path = None
            self._download()
        else:
            self._url = None
            self._path = url
            self._load()
        self._metadata = Metadata(self)
        # return a list of lists [[level, title, page, …], …]
        # self._doc.get_toc()

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
            if index != -1 and index != (len(url_path) - 1):
                filename = url_path[index+1:]
            else:
                raise NameError(f"Bad url {filename}")
            self._path = Path(self._cache_path).joinpath(filename)
        return self._path

    ##############################################

    def _download(self) -> None:
        # https://requests.readthedocs.io/en/latest/user/quickstart/#make-a-request
        # Fixme: missing timeout
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
        return self._doc

    ##############################################

    @property
    def metadata(self) -> 'Metadata':
        return self._metadata

    ##############################################

    @property
    def image_cache(self) -> PdfImageCache:
        if self._image_cache is None:
            self._image_cache = PdfImageCache(self)
        return self._image_cache

    ##############################################

    @property
    def number_of_pages(self) -> int:
        return self._doc.page_count

    def __len__(self) -> int:
        return self._doc.page_count

    ##############################################

    def _load_page(self, page_number: int) -> PdfPage:
        # if not from_zero:
        #     page_number -= 1
        if page_number < len(self):
            # for page in doc:
            # for page in reversed(doc):
            # for page in doc.pages(start, stop, step):
            fitz_page = self._doc[page_number]
            return PdfPage(self, page_number, fitz_page)
        else:
            raise ValueError(f"Out of page index {page_number}")

    ##############################################

    def _page(self, page_number: int) -> PdfPage:
        if page_number not in self._pages:
            page = self._load_page(page_number)
            self._pages[page_number] = page
            return page
        else:
            return self._pages[page_number]

    ##############################################

    @property
    def first_page(self) -> PdfPage:
        return self._page(0)

    ##############################################

    def __getitem__(self, slice_: int) -> PdfPage:
        # if isinstance(slice_, slice):
        #     return [self._page(i) for i in range(slice_.start, slice_.stop, slice_.step or 1)]
        # else:
        return self._page(slice_)

    def __iter__(self) -> Iterator[PdfPage]:
        for i in range(len(self)):
            yield self._page(i)

    ##############################################

    def iter_until(self, last_page: Optional[int] = None) -> Iterator[PdfPage]:
        if last_page is None:
            last_page = len(self) - 1
        for i in range(last_page + 1):
            yield self._page(i)

####################################################################################################

# class Metadata(ReadOnlyAttributeDictionaryInterface):
class Metadata():

    """ This class gives access to the PDF metadata.

    Public Attributes:

      :attr:`title`

      :attr:`subject`

      :attr:`author`

      :attr:`creator`

      :attr:`producer`

      :attr:`creation_date`

      :attr:`Mod_date`

    """

    # producer producer (producing software)
    # format format: ‘PDF-1.4’, ‘EPUB’, etc.
    # encryption encryption method used if any
    # author author
    # modDate date of last modification
    # keywords keywords
    # title title
    # creationDate date of creation
    # creator creating application
    # subject subject

    ##############################################

    def __init__(self, document: PdfDocument) -> None:
        self._document = document

        # self._title = doc.metadata['title']
        # self._author = doc.metadata['author']
        # self._creator = doc.metadata['creator']
        # self._creation_date = doc.metadata['creationDate']
        # self._modification_date = doc.metadata['modDate']
        # self._keywords = doc.metadata['keywords']
        # self._subject = doc.metadata['subject']

        # super().__init__()
        # for key in (
        #         'title',
        #         'subject',
        #         'author',
        #         'creator',
        #         'producer',
        #         'creationDate',
        #         'modDate',
        # ):
        #     self._dictionary[key] = document._doc.metadata[key]

    ##############################################

    def __getattr__(self, name: str) -> str:
        name = name.replace('D', '_d')
        return self._document._doc.metadata[name]
