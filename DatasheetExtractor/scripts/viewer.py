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

from DatasheetExtractor import setup_logging
setup_logging()

import logging

import os
os.environ['PYSIDE63_OPTION_PYTHON_ENUM'] = '1'
os.environ['QT_API'] = 'pyside6'
os.environ['QT_LOGGING_RULES'] = ';'.join((
    '*.debug=true',
    'qt.*.debug=false',
    '*.info=true',
))

from DatasheetExtractor.frontend.Application import Application

####################################################################################################

def main() -> None:
    logging.info('Start ...')
    # application = Application()
    Application.setup_gui_application()
    application = Application.create()
    application.exec_()
