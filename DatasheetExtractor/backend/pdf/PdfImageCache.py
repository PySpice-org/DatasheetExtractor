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

import numpy as np

from DatasheetExtractor.common.LruCache import LruCache

####################################################################################################

class Image:

    ##############################################

    def __init__(self, key: str, pixmap: np.ndarray) -> None:
        self._key = key
        self.pixmap = pixmap

    ##############################################

    def key(self) -> str:
        return self._key

    ##############################################

    def size(self) -> int:
        return self.pixmap.nbytes

####################################################################################################

class PdfImageCache:

    # Fixme: __XXX__
    antialiasing_level = 8
    cache_size = 128 * 1024 # Fixme: MB

    ##############################################

    def __init__(self, document, cache_size=cache_size):

        self._lru_cache = LruCache(constraint=cache_size)
        self._document = document

    ##############################################

    def to_pixmap(self,
                  page_index,
                  rotation=0,
                  resolution=72,
                  width=None, height=None, fit=False,
                 ):

        key = '-'.join([str(x) for x in (page_index,
                                         rotation,
                                         resolution,
                                         width, height, fit,
                                         self.antialiasing_level)])

        obj = self._lru_cache.acquire(key)
        if obj is not None:
            return obj.pixmap
        else:
            page = self._document[page_index]
            pixmap = page.to_pixmap(rotation,
                                    resolution,
                                    width, height, fit,
                                    self.antialiasing_level,
                                   )
            obj = Image(key, pixmap)
            self._lru_cache.add(obj)
            return pixmap
