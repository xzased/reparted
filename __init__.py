from ctypes.util import find_library
from ctypes import *

lib = find_library("parted")

if not lib:
    raise Exception("It's not a toomah!")

parted = CDLL(lib)

