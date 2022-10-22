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
#
#                                              Audit
#
# - 17/06/2013 Fabrice
#   attribute -> _attribute
#
####################################################################################################

####################################################################################################

import hashlib

from Babel.backend.Tools.DictionaryTools import DictInitialised

####################################################################################################

class TextStyle(DictInitialised):

    """

    Public Attributes:

      :attr:`font_family`

      :attr:`font_size`

      :attr:`id`

      :attr:`is_bold`

      :attr:`is_italic`

      :attr:`rank` font size rank, where 0 is the largest font size.

    """

    __REQUIRED_ATTRIBUTES__ = (
        'font_family',
        'font_size',
    )

    __DEFAULT_ATTRIBUTES__ = dict(
        is_bold=False,
        is_italic=False,
        rank=None, # font size rank, rank 0 for the largest
    )

    ##############################################

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        mangled_id = '{0.font_family}/{0.font_size}/{0.is_bold}/{0.is_italic}'.format(self)
        self.id = hashlib.sha1(mangled_id.encode('utf-8')).hexdigest()

    ##############################################

    def __lt__(self, other):

        return self.font_size < other.font_size

    ##############################################

    def __str__(self):

        template = """
Style ID {0.id}
  rank        {0.rank}
  font family {0.font_family}
  font size   {0.font_size}
  bold        {0.is_bold}
  italic      {0.is_italic}
""" # :.2f

        return template.format(self)

    ##############################################

    def __hash__(self):
        return self.id

####################################################################################################

class TextStyles(dict):

    """
    """

    ##############################################

    def register_style(self, style):

        self[style.id] = style

    ##############################################

    def sort(self):

        """ Sort the styles by font size. """

        sorted_styles = sorted(self.values(), reverse=True)

        # Compute the font size rank
        rank = 0
        current_font_size = None
        for style in sorted_styles:
            # Fixme: better way?
            font_size = style.font_size
            if current_font_size is not None and font_size < current_font_size:
                rank += 1
            current_font_size = font_size
            style.rank = rank

####################################################################################################

class TextStyleFrequency(DictInitialised):

    """

    Public Attributes:

      :attr:`style_id`

      :attr:`count`

    """

    __REQUIRED_ATTRIBUTES__ = (
        'style_id',
        'count',
    )

    ##############################################

    def __lt__(self, other):

        return self.count < other.count

    ##############################################

    def __iadd__(self, count):

        self.count += count

####################################################################################################

class TextStyleFrequencies(dict):

    """
    """

    ##############################################

    def __init__(self):

        super(TextStyleFrequencies, self).__init__()

        self._sorted_frequencies = None

    ##############################################

    def __iter__(self):

        """ iterate from the most frequent to the less frequent font. """

        self._sort_if_required()

        return iter(self._sorted_frequencies)

    ##############################################

    def __iadd__(self, other):

        for style_id, count in other.items():
            self.fill(style_id, count)

        return self

    ##############################################

    def fill(self, style_id, count):

        if style_id in self:
            self[style_id] += count
        else:
            self[style_id] = count # TextStyleFrequency(style_id, count) ?

        self._sorted_frequencies = None

    ##############################################

    def _to_list(self):

        return [TextStyleFrequency(style_id=style_id, count=count)
                for style_id, count in self.items()]

    ##############################################

    def sort(self):

        self._sorted_frequencies = sorted(self._to_list(), reverse=True)

    ##############################################

    def _sort_if_required(self):

        if self._sorted_frequencies is None:
            self.sort()

    ##############################################

    def max(self):

        """ Return the :obj:`TextStyleFrequency` instance of the most frequent font. """

        self._sort_if_required()

        return self._sorted_frequencies[0]
