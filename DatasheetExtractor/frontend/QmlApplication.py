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

__all__ = ['QmlApplication']

####################################################################################################

# import datetime
import logging
import traceback

from qtpy.QtCore import Property, Signal, Slot, QObject, QUrl
from qtpy.QtQml import QmlElement, QmlUncreatable

from .ApplicationMetadata import ApplicationMetadata
from .QmlPdf import QmlPdf
from .QmlTabulaExtractor import QmlTabulaExtractor

# Hack for typing to get rid of circular import...
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .Application import Application

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

QML_IMPORT_NAME = 'DatasheetExtractor'
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0   # Optional

####################################################################################################

@QmlElement
@QmlUncreatable('QmlApplication')
class QmlApplication(QObject):

    """Class to implement a Qt QML Application."""

    _logger = _module_logger.getChild('QmlApplication')

    ##############################################

    def __init__(self, application: 'Application') -> None:
        super().__init__()
        self._application = application
        self._pdf = None
        self._tabula_extractor = QmlTabulaExtractor()

    ##############################################

    show_message = Signal(str)   # message
    show_error = Signal(str, str)   # message backtrace

    def notify_message(self, message: str) -> None:
        self.show_message.emit(str(message))

    def notify_error(self, message: str) -> None:
        backtrace_str = traceback.format_exc()
        self.show_error.emit(str(message), backtrace_str)

    ##############################################

    @Property(str, constant=True)
    def application_name(self) -> str:
        return ApplicationMetadata.name

    @Property(str, constant=True)
    def application_url(self) -> str:
        return ApplicationMetadata.url

    @Property(str, constant=True)
    def about_message(self) -> str:
        return ApplicationMetadata.about_message()

    ##############################################

    # Signal to notify a pdf was passed as argument
    pdf_at_startup = Signal('QUrl')

    pdf_changed = Signal()

    @Property(QmlPdf, notify=pdf_changed)
    def pdf(self) -> QmlPdf:
        # return null if None
        return self._pdf

    @Slot('QUrl')
    def load_pdf(self, url: QUrl) -> None:
        # startup -> Application._post_init -> emit pdf_at_startup
        path = url.toString(QUrl.FormattingOptions(QUrl.RemoveScheme))
        self._logger.info('Load pdf {path} ...')
        self._pdf = QmlPdf(path)
        self._logger.info('Pdf loaded')
        # Fixme: use signal to propagate a new path ?
        self._tabula_extractor.path = path
        self.pdf_changed.emit()

    ##############################################

    @Property(QmlTabulaExtractor, constant=True)
    def tabula_extractor(self) -> QmlTabulaExtractor:
        return self._tabula_extractor
