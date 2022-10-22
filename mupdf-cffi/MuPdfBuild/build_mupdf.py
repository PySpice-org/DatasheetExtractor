####################################################################################################
#
# Babel - An Electronic Document Management System
# Copyright (C) 2014 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

####################################################################################################

import os
import re

####################################################################################################

from cffi import FFI
ffi = FFI()

from ctypes.util import find_library as _find_library
# from util import _find_library

####################################################################################################

mupdf_library = None
libraries = ['mupdf']

# First if there is an environment variable pointing to the library
if 'MUPDF_LIBRARY_PATH' in os.environ:
    mupdf_library_path = os.path.realpath(os.environ['MUPDF_LIBRARY_PATH'])
    library_path = os.path.join(mupdf_library_path, 'libmupdf.a') # Fixme: Linux
    if os.path.exists(library_path):
        mupdf_library = library_path
        libraries = ['mupdf', 'mupdfthird']
elif 'MUPDF_SHARED_LIBRARY' in os.environ:
    library_path = os.path.realpath(os.environ['MUPDF_SHARED_LIBRARY'])
    if os.path.exists(library_path):
        mupdf_library = library_path

# Else, try to find it
# search for shared library
if mupdf_library is None:
    library_name = 'mupdf'
    mupdf_library = _find_library(library_name)

# search for static library
if mupdf_library is None:
    for path in (
            # Fixme: Linux
            '/usr/lib64/libmupdf.a',
            '/usr/local/lib/libmupdf.a',
    ):
        if os.path.exists(path):
            mupdf_library = path
            libraries = ['mupdf', 'mupdfthird'] # Fixme: depend how it was compiled ...

# Else, we failed and exit
if mupdf_library is None:
    raise OSError('MUPDF library not found')
else:
    print('Found MuPDF library {}'.format(mupdf_library))

mupdf_library_path = os.path.dirname(mupdf_library)
mupdf_include_path = os.path.join(os.path.dirname(mupdf_library_path), 'include')
freetype_include_path = '/usr/include/freetype2' # Fixme: Linux

mupdf_version = None
version_path = os.path.join(mupdf_include_path, 'mupdf', 'fitz', 'version.h')
with open(version_path) as fh:
    for line in fh.readlines():
        regexp = re.compile('#define FZ_VERSION "(.*)"')
        match = regexp.match(line)
        if match is not None:
            mupdf_version = match.group(1)
            break
if mupdf_version is not None:
    print('MuPDF is {}'.format(mupdf_version))
else:
    raise NameError("MuPDF version not found")

####################################################################################################

module_path = os.path.dirname(__file__)

source = """
#include <sys/types.h>
#include <mupdf/fitz.h>

#include "fitz-extension.h"
#include "fitz-extension.c"

const char * MUPDF_VERSION = FZ_VERSION;
""" # .format(mupdf_version)
ffi.set_source(
    '_mupdf',
    source,
    include_dirs=[mupdf_include_path, module_path, freetype_include_path],
    library_dirs=[mupdf_library_path],
    libraries=libraries,
)

# Parse header
source = '''
static const char * MUPDF_VERSION;
'''
for file_name in ('mupdf-api.h', 'fitz-extension-api.h'):
    api_path = os.path.join(module_path, file_name)
    with open(api_path, 'r') as f:
        source += f.read()
ffi.cdef(source)

####################################################################################################

if __name__ == "__main__":
    ffi.compile()
