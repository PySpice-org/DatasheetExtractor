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
import os

from invoke import task

from .lib.MaterialIcon import MaterialIconFetcher

####################################################################################################

SOURCE_PATH = Path(__file__).resolve().parents[1]
ICONS_PATH = SOURCE_PATH.joinpath('DatasheetExtractor', 'frontend', 'rcc', 'icons')

####################################################################################################

@task
def fetch_icon(ctx, src_name, dst_name=None, style='baseline', color='black', version=12):
     # style: [baseline], outline, round, twotone, sharp
     # color: [black], white
    theme = 'material'
    print('Icons path:', ICONS_PATH, theme)
    if dst_name is None:
        dst_name = src_name.replace('_', '-')
    print(f'{src_name} -> {dst_name}   style={style} color={color} version={version}')
    fetcher = MaterialIconFetcher(ICONS_PATH, theme)
    fetcher.fetch_icon(
        src_name,
        dst_name or src_name.replace('_', '-'),
        style,
        color,
        version
    )

####################################################################################################

@task
def fix_name(ctx):
    for directory, _, filenames in os.walk(ICONS_PATH):
        directory = Path(directory)
        for filename in filenames:
            path = directory.joinpath(filename)
            if path.suffix == '.png':
                if '_' in filename:
                    new_filename = filename.replace('_', '-')
                    new_path = directory.joinpath(new_filename)
                    print(path, new_path)
                    path.rename(new_path)
