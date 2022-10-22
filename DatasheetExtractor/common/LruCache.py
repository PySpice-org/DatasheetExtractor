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

"""This module implements a Least Recently Used cache using a bidirectional linked list.

"""

####################################################################################################

__all__ = ['LruCache']

####################################################################################################

from typing import Any, Iterator
import logging

####################################################################################################

# from .backend.Math.Functions import rint

####################################################################################################

def rint(f: float) -> int:
    return int(round(f))

def inverse_percent(x: int) -> int:
    return 100 * x

####################################################################################################

class ObjectProtocol:

    """ This class defines the Object Protocol. """

    ##############################################

    def key(self) -> str:
        """ Return the object key. """
        raise NotImplementedError

    ##############################################

    def size(self) -> int:
        """ Return the object size. """
        raise NotImplementedError

####################################################################################################

class CacheElement:

    """ This class implements a cache element of the LRU cache. """

    _logger = logging.getLogger(__name__)

    ##############################################

    def __init__(self, cache_manager: 'LruCache', obj: Any, acquire: bool = False) -> None:
        """The stored object must implement the Object Protocol defined by the abstract class
        :class:`ObjectProtocol`.

        The reference counter is set to one if the *acquire* flag is set.

        """
        self._cache_manager = cache_manager
        self._obj = obj
        self.key = obj.key()
        self._size_in_cache = obj.size()
        self._reference_counter = 1 if acquire else 0
        self._younger = None
        self._older = None

    ##############################################

    def __del__(self) -> None:
        """Delete the stored object reference."""
        self._logger.debug('Delete CacheElement {self.key}')   # + str(self._obj)

    ##############################################

    def acquire(self) -> Any:
        """Increment the reference counter and return the stored object."""
        self._reference_counter += 1
        return self._obj

    ##############################################

    def release(self) -> None:
        """Decrement the reference counter."""
        self._reference_counter -= 1

    ##############################################

    def detach(self) -> None:
        """Delete the data object reference."""
        self._logger.debug('Detach CacheElement %s', str(self._obj))
        # !# self._obj.free()
        del self._obj

####################################################################################################

class LruCache:

    """ This class implements the LRU cache. """

    _logger = logging.getLogger(__name__)

    ##############################################

    def __init__(self, constraint: int) -> None:
        self._constraint = constraint
        self._cache_dict = {}
        self._younger = None   # reference to the younger element
        self._older = None   # reference to the older element
        self._size = 0

    ##############################################

    @property
    def constraint(self) -> int:
        """ Cache constraint. """
        return self._constraint

    @constraint.setter
    def constraint(self, constraint: int) -> None:
        self._constraint = constraint

    ##############################################

    def __len__(self) -> int:
        """Return the number of elements in the cache."""
        return len(self._cache_dict)

    ##############################################

    def size(self) -> int:
        """Return the cache size."""
        return self._size

    ##############################################

    def __iter__(self) -> Iterator[CacheElement]:
        """Iterate over the cache elements from the younger to the older."""
        cache_element = self._younger
        while cache_element is not None:
            yield cache_element
            cache_element = cache_element._older

    ##############################################

    def reset(self) -> None:
        # Fixme: reset -> clear ?
        """Reset the cache."""
        # Break all the references and clear the dict
        self._younger = None
        self._older = None
        for cache_element in self._cache_dict.values():
            del cache_element._younger
            del cache_element._older
        self._cache_dict.clear()

    ##############################################

    def _push_element(self, cache_element: CacheElement) -> None:
        """Push the element on top of the bidirectional linked list."""
        # if the list is empty set older reference
        if self._older is None:
            self._older = cache_element
        # Push the element on top of the list
        old_younger, self._younger = self._younger, cache_element
        if old_younger is not None:
            old_younger._younger = cache_element
        cache_element._older = old_younger
        cache_element._younger = None

    ##############################################

    def _unlink_element(self, cache_element: CacheElement) -> None:
        """Unlink an element from the bidirectional linked list."""
        older = cache_element._older
        younger = cache_element._younger
        if younger is None:
            # was the top element in the list
            self._younger = older
        else:
            younger._older = older
        if older is None:
            # was the bottom element in the list
            self._older = younger
        else:
            older._younger = younger

    ##############################################

    def recycle(self) -> None:
        """Recycle the cache."""
        size_to_recover = self._size - self._constraint
        self._logger.debug('Recycle: Size to recover %u', size_to_recover)
        cache_element = self._older
        while self._size > self._constraint and cache_element is not None:
            if not cache_element._reference_counter:
                self._unlink_element(cache_element)
                del self._cache_dict[cache_element.key]
                self._size -= cache_element._size_in_cache
                cache_element.detach()   # so as to decrease the reference counter
            cache_element = cache_element._younger
            # unlinked cache_element should be deleted now by the garbage collector
        # gc.collect()

    ##############################################

    def add(self, obj: Any, acquire: bool = False) -> None:
        """Add an object *obj* in the cache, cf. :class:`CacheElement`."""
        cache_element = CacheElement(self, obj, acquire)
        self._size += cache_element._size_in_cache
        self._cache_dict[cache_element.key] = cache_element
        self._push_element(cache_element)

    ##############################################

    def remove(self, key: str) -> None:
        """Remove an object referenced by its key."""
        if key in self._cache_dict:
            cache_element = self._cache_dict[key]
            self._size -= cache_element.size_in_cache
            self._unlink_element(cache_element)
            del self._cache_dict[key]

    ##############################################

    def acquire(self, key: str) -> Any | None:
        """Acquire an object referenced by its key. The object is moved on top of the list and its
        reference counter is incremented. Return the :class:`CacheElement` instance or :obj:`None`
        if the element is not found.

        """
        if key in self._cache_dict:
            cache_element = self._cache_dict[key]
            self._unlink_element(cache_element)
            self._push_element(cache_element)
            return cache_element.acquire()
        else:
            return None

    ##############################################

    def release(self, key: str) -> None:
        """Release an object referenced by its key. Its reference counter is decremented."""
        if key in self._cache_dict:
            cache_element = self._cache_dict[key]
            cache_element.release()

    ##############################################

    def __str__(self) -> str:
        percent = rint(inverse_percent(self._size / float(self._constraint)))
        text = f"""LRU cache:
  size = {self._size} / {self._constraint} = {percent} %%
  from the younger to the older
"""
        i = 0
        for cache_element in self:
            key = str(cache_element.key)
            rc = cache_element._reference_counter
            size = cache_element._size_in_cache
            obj = str(cache_element._obj)
            text += f'  [i:4] key={key} rc={rc} size={size} obj={obj}\n'
            i += 1
        return text
