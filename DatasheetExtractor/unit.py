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

__all__ = [
    'in2mm',
    'in2pt',
    'mm2in',
    'mm2pt',
    'pt2in',
    'pt2mm',
]

####################################################################################################

_IN_SCALE = 25.4   # mm
# The PDF specification defines PDF units as 72 PDF units to 1 inch.
_PT_SCALE = 72

####################################################################################################

def mm2in(_: int | float) -> float:
    return _ / _IN_SCALE

def in2mm(_: int | float) -> float:
    return _ * _IN_SCALE

def pt2in(_: int | float) -> float:
    return _ / _PT_SCALE

def pt2mm(_: int | float) -> float:
    return _ / _PT_SCALE * _IN_SCALE

def in2pt(_: int | float) -> float:
    return _ * _PT_SCALE

def mm2pt(_: int | float) -> float:
    return _ / _IN_SCALE * _PT_SCALE
