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
    "%":    1        # Fuck you pyparted, we've got percents!!!
}

class Size(object):
    def __init__(self, dev, length, units="MB"):
        self.__length = length
        self.units = units
        self.sector_size = dev.sector_size
        if units == "%":
            if not (0 < length <= 100) or type(length) is float:
                raise ValueError("%i%% is invalid" % length)
            self.sectors = (dev.length / 100) * length
        else:
            self.sectors = (size_units[units] * length) / self.sector_size

    def to(self, units):
        return size_units[units] * self.sectors

    def pretty(self, units="MB"):
        sz = ((float(self.sectors) * self.sector_size) / size_units[units])
        return "%.2f%s" % (sz, units)

    def __str__(self):
        return self.pretty()