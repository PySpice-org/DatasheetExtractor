export DatasheetExtractor_source_path=${PWD}
export DatasheetExtractor_examples_path=${DatasheetExtractor_source_path}/examples

source /opt/python-virtual-env/py310/bin/activate
append_to_python_path_if_not ${DatasheetExtractor_source_path}
