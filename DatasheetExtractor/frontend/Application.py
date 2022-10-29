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

"""Module to implement a Qt Application.

"""

####################################################################################################

__all__ = ['Application']

####################################################################################################

# import datetime
from pathlib import Path
import argparse
import logging
import os
import sys
import traceback

# We use https://github.com/spyder-ide/qtpy Qt shim
import qtpy
from qtpy import QtCore
from qtpy.QtCore import (
    qInstallMessageHandler, QtMsgType, QMessageLogContext,
    QTranslator,
    QObject,
    QTimer, QUrl, QThreadPool, QLocale,
)
from qtpy.QtGui import QIcon
from qtpy.QtQml import QQmlApplicationEngine
from qtpy.QtWidgets import QApplication
# from qtpy.QtQuickControls2 import QQuickStyle

from DatasheetExtractor.common.ArgparseAction import PathAction
from DatasheetExtractor.common.platform import QtPlatform
from .ApplicationMetadata import ApplicationMetadata
from .QmlApplication import QmlApplication
from .QmlPdf import PageImageProvider

# Load Resources
from .rcc import resources

# Register for QML
from .KeySequenceEditor import KeySequenceEditor

####################################################################################################

_module_logger = logging.getLogger(__name__)
_module_logger.info('Qt binding is %s %s', qtpy.API_NAME, QtCore.__version__)

def _make_module_url() -> list[Path]:
    file_path = Path(__file__)
    return [f'file://{_}/' for _ in [p.parents[1] for p in (file_path, file_path.resolve())]]
_MODULE_URLS = _make_module_url()

####################################################################################################

# Fixme: why not derive from QGuiApplication ???
class Application(QObject):

    """Class to implement a Qt Application."""

    instance = None

    _logger = _module_logger.getChild('Application')

    ##############################################

    @classmethod
    def setup_gui_application(self) -> None:
        # https://bugreports.qt.io/browse/QTBUG-55167
        # for path in (
        #         'qt.qpa.xcb.xcberror',
        # ):
        #     QLoggingCategory.setFilterRules('{} = false'.format(path))
        # QQuickStyle.setStyle('Material')
        pass

    ##############################################

    # Fixme: Singleton

    @classmethod
    def create(cls, *args: list, **kwargs: dict) -> 'Application':
        if cls.instance is not None:
            raise NameError('Instance exists')
        cls.instance = cls(*args, **kwargs)
        return cls.instance

    ##############################################

    def __init__(self) -> None:
        self._logger.info('Ctor')
        super().__init__()

        self._parse_arguments()

        if not self._args.no_qt_message_handler:
            qInstallMessageHandler(self._message_handler)

        # For Qt Labs Platform native widgets
        # self._application = QGuiApplication(sys.argv)
        # use QCoreApplication::instance() to get instance
        self._application = QApplication(sys.argv)
        #! self._application.main = self

        self._init_application()

        # combines a QQmlEngine and QQmlComponent
        # to provide a convenient way to load a single QML file
        self._engine = QQmlApplicationEngine()

        self._qml_application = QmlApplication(self)
        #! self._application.qml_main = self._qml_application

        self._platform = QtPlatform()
        # self._logger.info('\n' + str(self._platform))

        self._thread_pool = QThreadPool()
        number_of_threads_max = self._thread_pool.maxThreadCount()
        self._logger.info(f'Multithreading with maximum {number_of_threads_max} threads')

        self._page_image_provider = PageImageProvider()
        self._engine.addImageProvider('page_image', self._page_image_provider)

        self._translator = None
        # self._load_translation()
        self._set_context_properties()
        self._load_qml_main()

        QTimer.singleShot(0, self._post_init)

        # if isinstance(self._application, QGuiApplication):
        #     self._view = QQuickView()
        #     self._view.setResizeMode(QQuickView.SizeRootObjectToView)
        #     # self._view.setSource(qml_url)
        #     if self._view.status() == QQuickView.Error:
        #         sys.exit(-1)
        # else:
        #     self._view = None

    ##############################################

    # @property
    # def args(self):
    #     return self._args

    @property
    def platform(self) -> QtPlatform:
        return self._platform

    @property
    def qml_application(self) -> QmlApplication:
        return self._qml_application

    @property
    def thread_pool(self) -> QThreadPool:
        return self._thread_pool

    @property
    def page_image_provider(self) -> PageImageProvider:
        return self._page_image_provider

    ##############################################

    def _parse_arguments(self) -> None:
        parser = argparse.ArgumentParser(
            description='DatasheetExtractor',
        )
        parser.add_argument(
            '--no-qt-message-handler',
            action='store_true',
            default=False,
            help="don't install Qt message handler",
        )
        # parser.add_argument(
        #     '--version',
        #     action='store_true', default=False,
        #     help="show version and exit",
        # )
        # Fixme: should be able to start application without !!!
        parser.add_argument(
            'path', metavar='PATH',
            action=PathAction,
            help='pdf or library path',
        )
        parser.add_argument(
            '--dont-translate',
            action='store_true',
            default=False,
            help="Don't translate application",
        )
        parser.add_argument(
            '--user-script',
            action=PathAction,
            default=None,
            help='user script to execute',
        )
        parser.add_argument(
            '--user-script-args',
            default='',
            help="user script args (don't forget to quote)",
        )
        self._args = parser.parse_args()

    ##############################################

    def _print_critical_message(self, message: str) -> None:
        # print('\nCritical Error on {}'.format(datetime.datetime.now()))
        # print('-'*80)
        # print(message)
        self._logger.critical(message)

    ##############################################

    def _message_handler(self, msg_type: QtMsgType, context: QMessageLogContext, msg: str) -> None:
        match msg_type:
            case QtMsgType.QtDebugMsg:
                method = self._logger.debug
            case QtMsgType.QtInfoMsg:
                method = self._logger.info
            case QtMsgType.QtWarningMsg:
                method = self._logger.warning
            case QtMsgType.QtCriticalMsg | QtMsgType.QtFatalMsg:
                method = self._logger.critical

        msg = str(msg)
        for _ in _MODULE_URLS:
            msg = msg.replace(_, '')

        # local_msg = msg.toLocal8Bit()
        # localMsg.constData()
        context_file = context.file
        if context_file is not None:
            path = Path(context_file)
            file_path = path.name
            # is_qml = path.suffix == '.qml'
        else:
            file_path = ''
            # is_qml = False

        sep = os.linesep + '  '
        if file_path:
            sep += '  '
        function = f' / {context.function}' if context.function else ''
        message = f'\033[1;34m{file_path}{function}\033[0m{sep}{msg}'   # context.line

        if method is not None:
            method(message)
        else:
            self._print_critical_message(message)

    ##############################################

    def _on_critical_exception(self, exception: Exception) -> None:
        message = str(exception) + '\n' + traceback.format_exc()
        self._print_critical_message(message)
        self._qml_application.notify_error(exception)
        # sys.exit(1)

    ##############################################

    def _init_application(self) -> None:
        # Define Organisation
        self._application.setOrganizationName(ApplicationMetadata.organisation_name)
        self._application.setOrganizationDomain(ApplicationMetadata.organisation_domain)

        # Define Application
        self._application.setApplicationName(ApplicationMetadata.name)
        self._application.setApplicationDisplayName(ApplicationMetadata.display_name)
        self._application.setApplicationVersion(ApplicationMetadata.version)

        # Set logo
        # logo_path = ':/icons/logo/logo-256.png'
        # self._application.setWindowIcon(QIcon(logo_path))

        # Set icon theme
        QIcon.setThemeName('material')

    ##############################################

    def _load_translation(self) -> None:
        if self._args.dont_translate:
            return
        # Fixme: ConfigInstall
        # directory = ':/translations'
        directory = str(Path(__file__).parent.joinpath('rcc', 'translations'))
        locale = QLocale()
        self._translator = QTranslator()
        if self._translator.load(locale, 'pdf-browser', '.', directory, '.qm'):
            self._application.installTranslator(self._translator)
        else:
            raise NameError(f'No translator for locale {locale.name()}')

    ##############################################

    def _set_context_properties(self) -> None:
        context = self._engine.rootContext()
        context.setContextProperty('application', self._qml_application)

    ##############################################

    def _load_qml_main(self) -> None:
        self._logger.info('Load QML...')

        qml_path = Path(__file__).parent.joinpath('qml')
        # qml_path = 'qrc:///qml'
        self._engine.addImportPath(str(qml_path))

        main_qml_path = qml_path.joinpath('main.qml')
        self._qml_url = QUrl.fromLocalFile(str(main_qml_path))
        # QUrl('qrc:/qml/main.qml')
        self._engine.objectCreated.connect(self._check_qml_is_loaded)
        self._engine.load(self._qml_url)

        self._logger.info('QML loaded')

    ##############################################

    def _check_qml_is_loaded(self, obj: QObject, url: QUrl) -> None:
        # See https://bugreports.qt.io/browse/QTBUG-39469
        if (obj is None and url == self._qml_url):
            sys.exit(-1)

    ##############################################

    def exec_(self) -> None:
        # if self._view is not None:
        #     self._view.show()
        self._logger.info('Start event loop')
        rc = self._application.exec()
        # Deleting the view before it goes out of scope is required
        # to make sure all child QML instances are destroyed in the correct order.
        # if self._view is not None:
        #     del self._view
        sys.exit(rc)

    ##############################################

    def _post_init(self) -> None:
        self._logger.info('Post Init...')
        pdf_path = Path(self._args.path)
        if pdf_path.exists():
            pdf_url = QUrl(f'file:{pdf_path}')
            self._qml_application.pdf_at_startup.emit(pdf_url)
        if self._args.user_script is not None:
            self.execute_user_script(self._args.user_script)
        self._logger.info('Post Init Done')

    ##############################################

    def execute_user_script(self, script_path: str) -> None:
        """Execute an user script provided by file *script_path* in a context where is defined a
        variable *application* that is a reference to the application instance.

        """
        script_path = Path(script_path).absolute()
        self._logger.info(f'Execute user script:\n  {script_path}')
        try:
            with open(script_path, encoding='utf-8') as fh:
                source = fh.read()
        except FileNotFoundError:
            self._logger.info(f'File {script_path} not found')
            sys.exit(1)
        try:
            bytecode = compile(source, script_path, 'exec')
        except SyntaxError as exception:
            self._on_critical_exception(exception)
        try:
            exec(bytecode, {'application': self})
        except Exception as exception:
            self._on_critical_exception(exception)
        self._logger.info('User script done')
