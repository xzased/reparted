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
        return size_units[units] * self.sectors

    def pretty(self, units="MB"):
        sz = ((float(self.sectors) * self.sector_size) / size_units[units])
        return "%.2f%s" % (sz, units)

    def __str__(self):
        return self.pretty()