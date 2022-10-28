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

# Code inspired from
#  https://www.twobitarcade.net/article/multithreading-pyqt-applications-with-qthreadpool

####################################################################################################

__all__ = ['Worker']

####################################################################################################

import logging
# import sys
import traceback
from typing import Callable

####################################################################################################

from qtpy.QtCore import QRunnable, Signal, Slot, QObject

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class WorkerSignals(QObject):

    """Class to define the signals available from a running worker thread.

    .. note:: signals can only be defined on objects derived from QObject.

    Supported signals are:

    done
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
         int

    """

    done = Signal()
    error = Signal(tuple)
    result = Signal(str)   # Fixme: object
    progress = Signal(int)

####################################################################################################

class Worker(QRunnable):

    """Class to implement a worker thread.

    .. note:: non-GIL-releasing Python code can only execute in one thread at a time.

    :param callback: The function callback to run on this worker thread.
                     Supplied args and kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    """

    _logger = _module_logger.getChild('Worker')

    ##############################################

    def __init__(self, callback: Callable, *args: list, **kwargs: dict) -> None:
        super().__init__()
        self._callback = callback
        self._args = args
        self._kwargs = kwargs
        self._signals = WorkerSignals()

    ##############################################

    @property
    def signals(self) -> Signal:
        return self._signals

    ##############################################

    @Slot()
    def run(self) -> None:
        self._logger.info(f'run {self._callback}({self._args}, {self._kwargs})')
        try:
            result = self._callback(
                *self._args, **self._kwargs,
                # status=self._signals.status,
                # progress=self._signals.progress,
            )
        except Exception:
            traceback.print_exc()
            # exctype, value = sys.exc_info()[:2]
            self._logger.info('emit error')
            # Fixme: (exctype, value, traceback.format_exc())
            self._signals.error.emit()
        else:
            self._logger.info(f'emit result {result}')
            self._signals.result.emit(result)
        finally:
            self._logger.info('emit done')
            self._signals.done.emit()
