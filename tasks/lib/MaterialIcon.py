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

# https://material.io/tools/icons/static/icons/baseline-save-24px.svg
# https://material.io/tools/icons/static/icons/baseline-save-black-36.zip

# https://material.io/tools/icons/static/icons/outline-save-black-36.zip
# https://material.io/tools/icons/static/icons/round-save-black-36.zip
# https://material.io/tools/icons/static/icons/sharp-save-black-36.zip
# https://material.io/tools/icons/static/icons/twotone-save-black-36.zip

# https://material.io/tools/icons/static/icons/baseline-save-white-36.zip

# 1x/baseline_save_black_18dp.png: PNG image data, 18 x 18, 8-bit gray+alpha, non-interlaced
# 1x/baseline_save_black_24dp.png: PNG image data, 24 x 24, 8-bit gray+alpha, non-interlaced
# 1x/baseline_save_black_36dp.png: PNG image data, 36 x 36, 8-bit gray+alpha, non-interlaced
# 1x/baseline_save_black_48dp.png: PNG image data, 48 x 48, 8-bit gray+alpha, non-interlaced

# 2x/baseline_save_black_18dp.png: PNG image data, 36 x 36, 8-bit gray+alpha, non-interlaced
# 2x/baseline_save_black_24dp.png: PNG image data, 48 x 48, 8-bit gray+alpha, non-interlaced
# 2x/baseline_save_black_36dp.png: PNG image data, 72 x 72, 8-bit gray+alpha, non-interlaced
# 2x/baseline_save_black_48dp.png: PNG image data, 96 x 96, 8-bit gray+alpha, non-interlaced

####################################################################################################

from pathlib import Path
from zipfile import ZipFile
import os
import shutil
import tempfile
import urllib3

####################################################################################################

urllib3.disable_warnings()

####################################################################################################

class MaterialIconFetcher:

    BASE_URL = 'https://material.io/tools/icons/static/icons/'

    SCALE = (1, 2)
    DP = (18, 24, 36, 48)

    ##############################################

    def __init__(self, icons_path: str, theme: str) -> None:
        self._icons_path = Path(str(icons_path)).resolve()
        self._theme = str(theme)
        self._theme_path = self._icons_path.joinpath(self._theme)

        if not self._icons_path.exists():
            os.mkdir(self._icons_path)
        if not self._theme_path.exists():
            os.mkdir(self._theme_path)

        self._http = urllib3.PoolManager()

        # with tempfile.TemporaryDirectory() as tmp_directory:
        self._tmp_directory = tempfile.TemporaryDirectory()
        self._tmp_directory_path = Path(self._tmp_directory.name)
        print('tmp_directory', self._tmp_directory_path)

    ##############################################

    def _fetch_ressource(self, url: str) -> bytes:
        print('Fetch', url, '...')
        request = self._http.request('GET', url)
        return request.data

    ##############################################

    def _fetch_png_icon(self, **kwargs: dict) -> list[str, bytes]:
        # https://material.io/tools/icons/static/icons/baseline-save-black-36.zip
        url_pattern = '{style}-{name}-{color}-{dp}.zip'
        filename = url_pattern.format(**kwargs)
        url = self.BASE_URL + filename
        data = self._fetch_ressource(url)
        return filename, data

    ##############################################

    def _extract_png_archive(self, **kwargs: dict) -> None:
        filename, data = self._fetch_png_icon(**kwargs)
        zip_path = self._tmp_directory_path.joinpath(filename)
        with open(zip_path, 'wb') as fh:
            fh.write(data)
        with ZipFile(zip_path, 'r') as zip_archive:
            zip_archive.extractall(self._tmp_directory_path)

    ##############################################

    def fetch_icon(self, src_name: str, dst_name: str, style: str, color: str) -> None:
        kwargs = dict(src_name=src_name, dst_name=dst_name, style=style, color=color)

        for dp in self.DP:
            self._extract_png_archive(name=src_name, dp=dp, **kwargs)

        print()
        for scale in self.SCALE:
            for dp in self.DP:
                dst_kwargs = dict(kwargs)
                dst_kwargs.update(dict(scale=scale, dp=dp))

                # 1x/baseline_save_black_18dp.png
                filename_pattern = '{style}_{src_name}_{color}_{dp}dp.png'
                src_path = self._tmp_directory_path.joinpath(
                    '{scale}x'.format(**dst_kwargs),
                    filename_pattern.format(**dst_kwargs),
                )

                if scale > 1:
                    size_directory = '{dp}x{dp}@{scale}'.format(**dst_kwargs)
                else:
                    size_directory = '{dp}x{dp}'.format(**dst_kwargs)
                size_path = self._theme_path.joinpath(size_directory)
                if not size_path.exists():
                    os.mkdir(size_path)
                filename_pattern = '{dst_name}-{color}.png'
                filename = filename_pattern.format(**dst_kwargs)
                dst_path = size_path.joinpath(filename)

                # print('Copy', src_path, dst_path)
                shutil.copyfile(src_path, dst_path)

                rcc_line = f'<file>icons/{self._theme}/{size_directory}/{filename}</file>'
                if dp != 36:
                    rcc_line = f'<!-- {rcc_line} -->'
                rcc_line = ' '*8 + rcc_line
                print(rcc_line)
