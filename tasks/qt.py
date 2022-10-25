####################################################################################################
#
# DatasheetExtractor - A Python library to extract data from datasheet
# Copyright (C) 2022 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
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

from pathlib import Path

from invoke import task

####################################################################################################

SOURCE_PATH = Path(__file__).absolute().parents[1]
RCC_PATH = SOURCE_PATH.joinpath('DatasheetExtractor', 'frontend', 'rcc')

####################################################################################################

@task
def clean(ctx):   # noqa:
    for _ in (
            'application.rcc',
            'resources.py',
    ):
        RCC_PATH.joinpath(_).unlink()

@task
def rcc(ctx):   # noqa:
    with ctx.cd(RCC_PATH):
        ctx.run('pyside6-rcc application.qrc -o resources.py')
