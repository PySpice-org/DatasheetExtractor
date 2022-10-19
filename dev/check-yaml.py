from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

file_path = 'microchip-AVR128DA.yaml'
with (open(file_path)) as fh:
    data = load(fh, Loader=Loader)
print(data)
