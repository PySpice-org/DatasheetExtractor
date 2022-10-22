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

# cf. PEP 396 -- Module Version Numbers https://www.python.org/dev/peps/pep-0396/
__version__ = ''

####################################################################################################

__all__ = [
    'setup_logging',
    'PdfDocument',
    'PdfPage',
]

####################################################################################################

from .logging import setup_logging
from .backend.pdf.document import PdfDocument
from .backend.pdf.page import PdfPage
