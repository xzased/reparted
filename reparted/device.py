#This file is part of reparted.

#reparted is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#reparted is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with reparted.  If not, see <http://www.gnu.org/licenses/>.

from conversion import *
from disk import *
from exception import DeviceError
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

standard_devices = [
    "/dev/hda",
    "/dev/hdb",
    "/dev/hdc",
    "/dev/hdd",
    "/dev/hde",
    "/dev/hdf",
    "/dev/hdg",
    "/dev/hdh",
    "/dev/sda",
    "/dev/sdb",
    "/dev/sdc",
    "/dev/sdd",
    "/dev/sde",
    "/dev/sdf"
]

def device_probe(path):
    if not os.path.exists(path):
        return False
    dev = device_get(path)
    if bool(dev):
        return dev
    else:
        return False

class Device(object):
    def __init__(self, path=None, dev=None):
        if path:
            self.__device = device_probe(path)
        elif dev:
            self.__device = dev
        else:
            self.__device = self._probe_ped_device()
        if not bool(self.__device):
            raise DeviceError(500)

    @property
    def _ped_device(self):
        return self.__device

    @property
    def length(self):
        return self.__device.contents.length

    @property
    def path(self):
        return self.__device.contents.path

    @property
    def model(self):
        return self.__device.contents.model

    @property
    def type(self):
        return device_type[self.__device.contents.type]

    @property
    def sector_size(self):
        return self.__device.contents.sector_size

    @property
    def phys_sector_size(self):
        return self.__device.contents.phys_sector_size

    @property
    def open_count(self):
        return self.__device.contents.open_count

    @property
    def read_only(self):
        return bool(self.__device.contents.read_only)

    @property
    def external_mode(self):
        return bool(self.__device.contents.path)

    @property
    def dirty(self):
        return bool(self.__device.contents.dirty)

    @property
    def boot_dirty(self):
        return bool(self.__device.contents.boot_dirty)

    @property
    def hw_geom(self):
        cylinders = self.__device.contents.hw_geom.cylinders
        heads = self.__device.contents.hw_geom.heads
        sectors = self.__device.contents.hw_geom.sectors
        return (cylinders, heads, sectors)

    @property
    def bios_geom(self):
        cylinders = self.__device.contents.bios_geom.cylinders
        heads = self.__device.contents.bios_geom.heads
        sectors = self.__device.contents.bios_geom.sectors
        return (cylinders, heads, sectors)

    @property
    def host(self):
        return self.__device.contents.host

    @property
    def did(self):
        return self.__device.contents.did

    def _probe_ped_device(self):
        for path in standard_devices:
            dev = device_probe(path)
            if bool(dev):
                return dev
        raise DeviceError(500)

def probe_standard_devices():
    devices = []
    for path in standard_devices:
        dev = device_probe(path)
        if dev:
            device = Device(dev=dev)
            devices.append(device)
    return devices