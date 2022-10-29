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

__all__ = ['backup_file']

####################################################################################################

import logging
from pathlib import Path

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

def backup_file(path: str | Path) -> None:
    path = Path(path)
    if path.exists():
        backup_path = Path(path)
        i = 1
        while backup_path.exists():
            backup_path = path.parent.joinpath(f'{path.name}.~{i}~')
            i += 1
        # Fixme: not atomic on OS
        # On Unix, if target exists and is a file, it will be replaced silently if the user has permission.
        # On Windows, if target exists, FileExistsError will be raised.
        _module_logger.warning(f'Rename {path} to {backup_path}')
        path.rename(backup_path)
