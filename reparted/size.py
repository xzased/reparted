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

from exception import SizeError

size_units = {
    "B":    1,       # byte
    "KB":   1000**1, # kilobyte
    "MB":   1000**2, # megabyte
    "GB":   1000**3, # gigabyte
    "TB":   1000**4, # terabyte
    "PB":   1000**5, # petabyte
    "EB":   1000**6, # exabyte
    "ZB":   1000**7, # zettabyte
    "YB":   1000**8, # yottabyte
    "KiB":  1024**1, # kibibyte
    "MiB":  1024**2, # mebibyte
    "GiB":  1024**3, # gibibyte
    "TiB":  1024**4, # tebibyte
    "PiB":  1024**5, # pebibyte
    "EiB":  1024**6, # exbibyte
    "ZiB":  1024**7, # zebibyte
    "YiB":  1024**8, # yobibyte
    "%":    1        # we've got percents!!!
}

class Size(object):
    """
    *Size class is used as a container to specify desired partition sizes.*

    You need to call this class before adding Partition instances.
    The default values for units is "MB" and sector_size is set to 512.
    You can manually specify the sector size or pass the device you intend
    to use it with and have it obtain the secdtor size from there::

        from reparted import *

        # sector size defaults to 512
        mySize1 = Size(4, "GB")

        # manually set the sector size to 1024
        mySize2 = Size(4, "GB", sector_size=1024)

        # get the sector size from the device
        myDevice = Device('/dev/sda')
        mySize = Size(4, "GB", myDevice)

    There is an option to choose percentage *'%'* as units, in which case
    you need to pass a Device instance to calculate the sectors needed
    and length should be between 1 and 100::

        from reparted import *

        myDevice = Device('/dev/sda')
        mySize = Size(25, "%", myDevice)

    *Args:*
        length (int):       The desired length.

        units (str):        The desired units (ie. "MB", "GB", "%" etc...)

        sector_size (int):  The sector size to be used to calculate.

        dev:                A Device instance. Only needed when using
                            percents, otherwise calculations will take
                            sector size from Device.sector_size.

    *Raises:*
        SizeError

    .. note::

       When using percent as unit and using the Size instance for multiple
       disks make sure they all have the same sector size.

    """
    def __init__(self, length, units="MB", sector_size=512, dev=None):
        self.__length = length
        self.units = units
        self.sector_size = getattr(dev, "sector_size", sector_size)
        if units != "%":
            self.sectors = (size_units[units] * length) / self.sector_size
        elif not dev:
            raise SizeError(400)
        elif not (0 < length <= 100) or type(length) is float:
            raise SizeError(401)
        else:
            self.sectors = (dev.length / 100) * length

    def to(self, units):
        """
        Returns the size in the specified units.

        *Args:*
            units (str):    The desired units (ie. "MB", "GB", "%" etc...)
        """
        sz = ((float(self.sectors) * self.sector_size) / size_units[units])
        return sz

    def pretty(self, units="MB"):
        """
        Returns the size in the specified units in a pretty string.

        *Args:*
            units (str):    The desired units (ie. "MB", "GB", "%" etc...)
        """
        sz = self.to(units)
        return "%.2f%s" % (sz, units)

    def __str__(self):
        return self.pretty()