####################################################################################################
#
# Babel - An Electronic Document Management System
# Copyright (C) 2014 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

####################################################################################################

from Babel.backend.Tools.LruCache import LruCache

####################################################################################################

class Image:

    ##############################################

    def __init__(self, key, pixmap):

        self._key = key
        self.pixmap = pixmap

    ##############################################

    def key(self):
        return self._key

    ##############################################

    def size(self):
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
