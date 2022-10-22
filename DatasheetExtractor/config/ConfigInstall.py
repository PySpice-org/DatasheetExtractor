####################################################################################################
#
# DatasheetExtractor - A Python library to extract data from datasheet
# Copyright (C) 2018 Fabrice Salvaire
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

__all__ = ['Path', 'Logging']

####################################################################################################

from pathlib import Path as plPath
import sys

####################################################################################################

from DatasheetExtractor.common import PathTools   # due to Path class

####################################################################################################

class OsFactory:

    ##############################################

    def __init__(self) -> None:
        if sys.platform.startswith('linux'):
            self._name = 'linux'
        elif sys.platform.startswith('win'):
            self._name = 'windows'
        elif sys.platform.startswith('darwin'):
            self._name = 'osx'

    ##############################################

    @property
    def name(self) -> str:
        return self._name

    @property
    def on_linux(self) -> bool:
        return self._name == 'linux'

    @property
    def on_windows(self) -> bool:
        return self._name == 'windows'

    @property
    def on_osx(self) -> bool:
        return self._name == 'osx'

OS = OsFactory()

####################################################################################################

_this_file = plPath(__file__).resolve()

class Path:
    module_directory = _this_file.parents[1]
    config_directory = _this_file.parent

####################################################################################################

class Logging:

    default_config_file = 'logging.yml'
    directories = (Path.config_directory,)

    ##############################################

    @staticmethod
    def find(config_file: str) -> plPath:
        return PathTools.find(config_file, Logging.directories)
