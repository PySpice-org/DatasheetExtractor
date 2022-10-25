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

from .lib.MaterialIcon import MaterialIconFetcher

####################################################################################################

SOURCE_PATH = Path(__file__).resolve().parents[1]
ICONS_PATH = SOURCE_PATH.joinpath('DatasheetExtractor', 'frontend', 'rcc', 'icons')

####################################################################################################

@task
def fetch_icon(ctx, src_name, dst_name, style='baseline', color='white'):
     # style: [baseline], outline, round, twotone, sharp
     # color: [black], white
    theme = 'material'
    print('Icons path:', ICONS_PATH, theme)
    fetcher = MaterialIconFetcher(ICONS_PATH, theme)
    fetcher.fetch_icon(
        src_name,
        dst_name or src_name.replace('_', '-'),
        style,
        color,
    )
