from conversion import *
from disk import *
import os

device_type = {
    0 : 'UNKNOWN',
    1 : 'SCSI',
    2 : 'IDE',
    3 : 'DAC960',
    4 : 'CPQARRAY',
    5 : 'FILE',
    6 : 'ATARAID',
    7 : 'I20',
    8 : 'UBD',
    9 : 'DASD',
    10 : 'VIODASD',
    11 : 'SX8',
    12 : 'DM',
    13 : 'XVD',
    14 : 'SDMMC',
    15 : 'VIRTBLK',
    16 : 'AOE',
    17 : 'MD',
}

class Device(object):
    def __init__(self, path=None, dev=None):
        if path:
            if not os.path.exists(path):
                raise Exception("%s does not exist" % path)
            self.__device = device_get(path)
        elif dev:
            self.__device = dev
        else:
            raise Exception("Dude WTF?")

        self.path = self.__device.contents.path
        self.model = self.__device.contents.model
        self.type = device_type[self.__device.contents.type]
        self.sector_size = self.__device.contents.sector_size

    def disk(self):
        return Disk(self, None)



