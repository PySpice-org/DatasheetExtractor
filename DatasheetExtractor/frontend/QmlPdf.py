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

__all__ = [
    'PageImageProvider',
    'QmlPdf',
    'QmlPdfMetadata',
    'QmlPdfPage',
]

####################################################################################################

from pathlib import Path
import glob
import logging
import subprocess
import time
import uuid

from PyQt5.QtGui import QPixmap
from PyQt5.QtQuick import QQuickImageProvider
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtQml import QQmlListProperty
from QtShim.QtCore import (
    Property, Signal, Slot, QObject,
    Qt, QTimer, QUrl
)

from PIL import ImageQt, Image

import markdown

#! from DatasheetExtractor.Thumbnail import FreeDesktopThumbnailCache # Fixme: Linux only
from DatasheetExtractor.backend.pdf.document import PdfDocument
#! from .Runnable import Worker

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

#! thumbnail_cache = FreeDesktopThumbnailCache()

####################################################################################################

class PageImageProvider(QQuickImageProvider):

    _logger = _module_logger.getChild('PageImageProvider')

    ##############################################

    def __init__(self):
        super().__init__(QQuickImageProvider.Image) # Pixmap
        self._output = None

    ##############################################

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, image):
        self._output = ImageQt.ImageQt(Image.fromarray(image))

    ##############################################

    def requestImage(self, image_id, size):
        self._logger.info('{} {}'.format(image_id, size))
        return self._output, self._output.size()

    ##############################################

    def requestPixmap(self, image_id, size):
        self._logger.info('{} {}'.format(image_id, size))
        pixmap = QPixmap(self._output.size())
        pixmap.convertFromImage(self._output)
        return pixmap, pixmap.size()

####################################################################################################

class QmlPdfMetadata(QObject):

    _logger = _module_logger.getChild('QmlPdfMetadata')

    ##############################################

    def __init__(self, pdf):
        super().__init__()
        self._pdf = pdf
        #! self._metadata = pdf.metadata
        self._dirty = False

    ##############################################

    @staticmethod
    def _to_list(value):
        return [x.strip() for x in value.split(',')]

    ##############################################

    @Property(str, constant=True)
    def path(self):
        return self._metadata.path_str

    ##############################################

    dirty_changed = Signal()

    @Property(bool, notify=dirty_changed)
    def dirty(self):
        return self._dirty

    def _set_dirty(self, value=True):
        if self._dirty != value:
            self._dirty = value
            self.dirty_changed.emit()

    ##############################################

    authors_changed = Signal()

    @Property(str, notify=authors_changed)
    def authors(self):
        return self._metadata.authors_str

    @authors.setter
    def authors(self, value):
        value = self._to_list(value)
        if self.authors != value:
            self._metadata.authors = value
            self.authors_changed.emit()
            self._set_dirty()

    ##############################################

    language_changed = Signal()

    @Property(str, notify=language_changed)
    def language(self):
        return self._metadata.language

    @language.setter
    def language(self, value):
        if self.language != value:
            self._metadata.language = value
            self.language_changed.emit()
            self._set_dirty()

    ##############################################

    number_of_pages_changed = Signal()

    @Property(int, notify=number_of_pages_changed)
    def number_of_pages(self):
        return self._metadata.number_of_pages

    @number_of_pages.setter
    def number_of_pages(self, value):
        if self.number_of_pages != value:
            self._metadata.number_of_pages = value
            self.number_of_pages_changed.emit()
            self._set_dirty()

    ##############################################

    publisher_changed = Signal()

    @Property(str, notify=publisher_changed)
    def publisher(self):
        return self._metadata.publisher

    @publisher.setter
    def publisher(self, value):
        if self.publisher != value:
            self._metadata.publisher = value
            self.publisher_changed.emit()
            self._set_dirty()

    ##############################################

    title_changed = Signal()

    @Property(str, notify=title_changed)
    def title(self):
        return self._metadata.title

    @title.setter
    def title(self, value):
        if self.title != value:
            self._metadata.title = value
            self.title_changed.emit()
            self._set_dirty()

    ##############################################

    year_changed = Signal()

    @Property(int, notify=year_changed)
    def year(self):
        return self._metadata.year

    @year.setter
    def year(self, value):
        if self.year != value:
            self._metadata.year = value
            self.year_changed.emit()
            self._set_dirty()

    ##############################################

    keywords_changed = Signal()

    @Property(str, notify=keywords_changed)
    def keywords(self):
        return self._metadata.keywords_str

    @keywords.setter
    def keywords(self, value):
        value = self._to_list(value)
        if self.keywords != value:
            self._metadata.keywords = value
            self.keywords_changed.emit()
            self._set_dirty()

    ##############################################

    description_changed = Signal()

    @Property(str, notify=description_changed)
    def description(self):
        return self._metadata.description

    @description.setter
    def description(self, value):
        if self.description != value:
            self._metadata.description = value
            self.description_changed.emit()
            self._set_dirty()

    ##############################################

    notes_changed = Signal()
    notes_html_changed = Signal()

    @Property(str, notify=notes_changed)
    def notes(self):
        return self._metadata.notes

    @Property(str, notify=notes_html_changed)
    def notes_html(self):
        return markdown.markdown(self._metadata.notes)

    @notes.setter
    def notes(self, value):
        if self.notes != value:
            self._metadata.notes = value
            self.notes_changed.emit()
            self.notes_html_changed.emit()
            self._set_dirty()

    ##############################################

    @Slot()
    def save(self):
        self._pdf.save_metadata()
        self._set_dirty(False)

####################################################################################################

class QmlPdfPage(QObject):

    _logger = _module_logger.getChild('QmlPdfPage')

    ##############################################

    def __init__(self, qml_pdf, pdf_page):
        super().__init__()
        self._qml_pdf = qml_pdf
        self._page = pdf_page
        self._text = None
        self._logger.info(f'Qml Page {self._page.number}')

    ##############################################

    def __repr__(self):
        return '{0} {1}'.format(self.__class__.__name__, self._page)

    ##############################################

    @property
    def page(self):
        return self._page

    ##############################################

    path_changed = Signal()

    @Property(str, notify=path_changed)
    def path(self):
        #! return str(self._page.path)
        return '...'

    ##############################################

    # @Property(int, constant=True)
    # def large_thumbnail_size(self):
    #     return FreeDesktopThumbnailCache.LARGE_SIZE

    # large_thumbnail_path_changed = Signal()

    # @Property(str, notify=large_thumbnail_path_changed)
    # def large_thumbnail_path(self):
    #     # Fixme: cache thumbnail instance ?
    #     return str(thumbnail_cache[self._page.path].large_path)

    ##############################################

    # thumbnail_ready = Signal()

    # @Slot()
    # def request_large_thumbnail(self):
    #     def job():
    #         # Fixme: issue when the application is closed
    #         return str(thumbnail_cache[self._page.path].large)
    #     worker = Worker(job)
    #     worker.signals.finished.connect(self.thumbnail_ready)
    #     from .QmlApplication import Application
    #     Application.instance.thread_pool.start(worker)

    ##############################################

    page_number_changed = Signal()

    @Property(int, notify=page_number_changed)
    def page_number(self):
        # return int(self._page)
        return self._page.number

    ##############################################

    @Slot(result=str)
    def generate_pixmap(self):
        self._logger.info(f'generate pixmap for page {self.page_number}')
        from .QmlApplication import Application
        image = self._page.pixmap()
        Application.instance.page_image_provider.output = image
        return str(uuid.uuid1())

        # def job():
        #     image = self._scanner.scan_image()
        #     Application.instance.page_image_provider.output = image
        #     return str(uuid.uuid1())

        # worker = Worker(job)
        # worker.signals.result.connect(self.preview_done)
        # # worker.signals.finished.connect()
        # # worker.signals.progress.connect()

        # from .QmlApplication import Application
        # Application.instance.thread_pool.start(worker)
            
    ##############################################

    # text_ready = Signal()

    # @Property(str, constant=True)
    # def text(self):

    #     if not self._ocr_running and self._text is None:
    #         metadata = self._page.pdf.metadata
    #         language = metadata.language or None

    #         def job():
    #             # Set fake to debug and receive a large lorem ipsum
    #             text = self._page.to_text(language, fake=False)
    #             # use result signal ???
    #             self._text = text
    #             # return text

    #         worker = Worker(job)
    #         worker.signals.finished.connect(self.text_ready)
    #         self._ocr_running = True
    #         from .QmlApplication import Application
    #         Application.instance.thread_pool.start(worker)

    #     return self._text

    ##############################################

    @Slot(QUrl)
    def save_text(self, url):
        path = url.toString(QUrl.RemoveScheme)
        try:
            with open(path, 'w') as fh:
                fh.write(self.text)
            self._logger.info('Save text page in {}'.format(path))
        except:
            application = QCoreApplication.instance()
            qml_application = application.qml_main
            tr_str = QCoreApplication.translate('QmlPdfPage', 'Could not save file {}')
            qml_application.notify_message(tr_str.format(path))

    ##############################################

    @Slot(str)
    def open_in_external_program(self, program):
        command = (program, self.path)
        self._logger.info(' '.join(command))
        process = subprocess.Popen(command)

####################################################################################################

class QmlPdf(QObject):

    new_page = Signal(int)

    _logger = _module_logger.getChild('QmlPdf')

    ##############################################

    def __init__(self, path):
        super().__init__()
        self._pdf = PdfDocument(path)
        self._metadata = QmlPdfMetadata(self._pdf)
        # We must prevent garbage collection
        self._pages = [QmlPdfPage(self, page) for page in self._pdf]

    ##############################################

    @Property(str, constant=True)
    def path(self):
        return str(self._pdf.path)

    ##############################################

    @Property(QmlPdfMetadata, constant=True)
    def metadata(self):
        return self._metadata

    ##############################################

    number_of_pages_changed = Signal()

    @Property(int, notify=number_of_pages_changed)
    def number_of_pages(self):
        # return self._pdf.number_of_pages
        return len(self._pages)

    @Slot(int, result=bool)
    def is_valid_page_number(self, page_number):
        return 0 < page_number <= self.number_of_pages

    ##############################################

    last_page_number_changed = Signal()

    @Property(int, notify=last_page_number_changed)
    def last_page_number(self):
        return self._pdf.last_page_number

    ##############################################

    pages_changed = Signal()

    @Property(QQmlListProperty, notify=pages_changed)
    def pages(self):
        return QQmlListProperty(QmlPdfPage, self, self._pages)

    ##############################################

    @Property(QmlPdfPage)
    def first_page(self):
        try:
            # return self._pages[0]
            return self._pages[1]
        except IndexError:
            return None

    @Property(QmlPdfPage)
    def last_page(self):
        try:
            return self._pages[-1]
        except IndexError:
            return None

    @Slot(int, result=QmlPdfPage)
    def page(self, page_number):
        try:
            # return self._pages[page_number-1]
            return self._pages[page_number]
        except IndexError:
            return None