# DatasheetExtractor
Tool to extract data from electronic component datasheet

# Python Dependencies

- IntervalArithmetic
- Markdown
- numpy
- pandas
- Pillow (import PIL)
- PyMuPDF (import fitz) https://pymupdf.readthedocs.io/en/latest/
  developed by Artifex
- PyYAML (import yaml)
- Pyside6
- Qtpy
- requests
- tabula-py https://github.com/chezou/tabula-py
  requires java-17-openjdk
- OpenCV opencv-python (import cv2) https://pypi.org/project/opencv-python

# Examples

- examples/im.py
  `ImportError: cannot import name '_core' from partially initialized module 'mamba' (most likely due to a circular import) (/home/fabrice/__projects__/datasheet-extractor/mamba-dist/mamba/__init__.py)`
- examples/test.py
  `ImportError: cannot import name 'PinoutExtractor' from 'DatasheetExtractor.backend.extractor' (/home/fabrice/__projects__/datasheet-extractor/DatasheetExtractor/backend/extractor/__init__.py)`
- examples/test-tabula.py OK

# Viewer

- PDF viewer
- processiong broken
