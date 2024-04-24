export DatasheetExtractor_source_path=${PWD}
export DatasheetExtractor_examples_path=${DatasheetExtractor_source_path}/examples

source /opt/python-virtual-env/py311/bin/activate

export PYTHONPYCACHEPREFIX=${DatasheetExtractor_source_path}/.pycache
export PYTHONDONTWRITEBYTECODE=${DatasheetExtractor_source_path}/.pycache

append_to_python_path_if_not ${DatasheetExtractor_source_path}
append_to_python_path_if_not ${DatasheetExtractor_source_path}/mamba-dist/
append_to_ld_library_path_if_not ${DatasheetExtractor_source_path}/mamba-dist/

# Fixme: libQt6PdfQuick.so.6
# append_to_ld_library_path_if_not /home/opt/python-virtual-env/py310/lib/python3.10/site-packages/PyQt6/Qt6/lib/
