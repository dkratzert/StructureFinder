import sys, pathlib

__version__ = 97

pth = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(pth))
