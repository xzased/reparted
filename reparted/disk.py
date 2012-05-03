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
from exception import *
import os

disk_features = {
    1 : 'EXTENDED',
    2 : 'PARTITION_NAME'
}

disk_labels = [
    "gpt",
    "msdos"
]

alignment_any = PedAlignment(0, 1)

partition_type = {
    0 : 'NORMAL',
    1 : 'LOGICAL',
    2 : 'EXTENDED',
    4 : 'FREESPACE',
    8 : 'METADATA',
    10 : 'PROTECTED'
}

partition_flag = {
    "BOOT" : 1,
    "ROOT" : 2,
    "SWAP" : 3,
    "HIDDEN" : 4,
    "RAID" : 5,
    "LVM" : 6,
    "LBA" : 7,
    "HPSERVICE" : 8,
    "PALO" : 9,
    "PREP" : 10,
    "MSFT_RESERVED" : 11,
    "BIOS_GRUB" : 12,
    "APPLE_TV_RECOVERY" : 13,
    "DIAG" : 14,
    "LEGACY_BOOT" : 15
}

def diskDecorator(error=False):
    def wrap(fn):
        def wrapped(self, *args, **kwargs):
            if bool(self._ped_disk):
                return fn(self, *args, **kwargs)
            if error:
                raise DiskError(606)
            return None
        return wrapped
    return wrap

class Disk(object):
    """
    *Disk class is used as a wrapper to libparted's ped_disk.*

    You need to call this class to list, add or delete partitions.
    A new instance of Disk is initialized by passing the Device instance::

        from reparted import *

        myDevice = Device("/dev/sda")
        myDisk = Disk(myDevice)

    *Args:*
        dev:    A Device class instance.

        disk:   A ped_disk pointer, usually this is used internally.

    *Raises:*
        DiskError

    .. note::

       You need to pass either a Device instance or a ped_disk pointer.
       If a disk is being initialized (no partition table) only the
       set_label method is available, with other methods returning
       None or raising DiskError.
    """
    def __init__(self, device=None, disk=None):
        if device:
            self.__device = device._ped_device
            self.__disk = disk_new(self.__device)
        elif disk:
            self.__disk = disk
            self.__device = self.__disk.contents.dev
        else:
            raise DiskError(600)

    @property
    def _ped_device(self):
        """
        Returns the ctypes ped_device pointer.
        """
        return self.__device

    @property
    def _ped_disk(self):
        """
        Returns the ctypes ped_disk pointer.
        """
        return self.__disk

    @property
    @diskDecorator()
    def type_name(self):
        """
        Returns the disk type (ie. 'gpt' or 'msdos').
        """
        return self.__disk.contents.type.contents.name

    @property
    @diskDecorator()
    def device(self):
        """
        Returns the Device the disk belongs to.
        """
        return self.__device

    @property
    @diskDecorator()
    def type_features(self):
        """
        Returns the features available (ie. 'EXTENDED' for
        lvm and 'PARTITION_NAME' for label support).
        """
        feat = self.__disk.contents.type.contents.features
        return disk_features[feat]

    @property
    @diskDecorator()
    def block_sizes(self):
        """
        Returns the disk block sizes.
        """
        return self.__disk.contents.block_sizes

    @property
    @diskDecorator()
    def needs_clobber(self):
        """
        Returns True if the disk needs clobber.
        """
        return bool(self.__disk.contents.needs_clobber)

    @property
    @diskDecorator()
    def update_mode(self):
        """
        Returns True if the disk is set to update mode.
        """
        return bool(self.__disk.contents.update_mode)

    @diskDecorator()
    def partitions(self):
        """
        Returns a list of the current disk partitions.

        .. note::

            If the disk is initialized (no partition table) it
            will return None, if the disk has a partition table
            but no partitions it will return an empty list.
        """
        partitions = []
        part = disk_next_partition(self.__disk, None)
        while part:
            if part.contents.type > 2:
                part = disk_next_partition(self.__disk, part)
                continue
            p = Partition(part=part)
            partitions.append(p)
            part = disk_next_partition(self.__disk, part)
        return partitions

    @diskDecorator(error=True)
    def add_partition(self, part):
        """
        Adds a partition to disk. You still need to call commit
        for the changes to be made to disk::

            from reparted import *

            myDevice = Device("/dev/sdb")
            myDisk = Disk(myDevice)
            mySize = Size(4, "GB")
            myPartition = Partition(myDisk, mySize)
            myDisk.add_partition(myPartition)
            myDisk.commit()

        *Args:*
            part:       A Partition class instance.

        *Raises:*
            AddPartitionError

        .. note::

            If the disk is initialized (no partition table) it
            will raise DiskError.
        """
        try:
            p = self.get_partition(part.num)
            if p.geom == part.geom:
                raise AddPartitionError(701)
        except ValueError:
            pass
        partition = part._Partition__partition
        disk = self.__disk
        start, end, length = part.geom
        range_start = geometry_new(self.__device, start, 1)
        range_end = geometry_new(self.__device, end, 1)
        user_constraint = constraint_new(alignment_any, alignment_any, range_start, range_end, 1, disk.contents.dev.contents.length)
        if not bool(user_constraint):
            raise AddPartitionError(702)
        if part.alignment == 'optimal':
            dev_constraint = device_get_optimal_aligned_constraint(self.__device)
        elif part.alignment == 'minimal':
            dev_constraint = device_get_minimal_aligned_constraint(self.__device)
        else:
            dev_constraint = device_get_constraint(self.__device)
        if not bool(dev_constraint):
            raise AddPartitionError(702)
        final_constraint = constraint_intersect(user_constraint, dev_constraint)
        constraint_destroy(user_constraint)
        constraint_destroy(dev_constraint)
        if not bool(final_constraint):
            raise AddPartitionError(703)
        added = disk_add_partition(disk, partition, final_constraint)
        constraint_destroy(final_constraint)
        if not added:
            disk_remove_partition(disk, partition)
            raise AddPartitionError(701)
        if part.name:
            set_name = partition_set_name(partition, part.name)
            if not set_name:
                disk_remove_partition(disk, partition)
                raise AddPartitionError(704)

    @diskDecorator(error=True)
    def delete_partition(self, part):
        """
        Deletes a partition from disk. Unlike add_partition,
        this method calls commit, use carefully::

            from reparted import *

            myDevice = Device("/dev/sdb")
            myDisk = Disk(myDevice)

            # Get Partition instance and remove it.
            part = myDisk.partitions()[0]
            myDisk.delete_partition(part)

            # Get Partition number and remove it.
            part = myDisk.partitions()[0].num
            myDisk.delete_partition(part)

        *Args:*
            part:   A Partition class instance OR partition number.

        *Raises:*
            DeletePartitionError, DiskCommitError

        .. note::

            If the disk is initialized (no partition table) it
            will raise DiskError.
        """
        if part and isinstance(part, Partition):
            partition = part._Partition__partition
        elif type(part) is int:
            partition = self._get_ped_partition(part)
        else:
            raise DeletePartitionError(705)
        if partition_is_busy(partition):
            raise DeletePartitionError(706)
        disk_delete_partition(self.__disk, partition)
        self.commit()
        disk_destroy(self.__disk)
        self.__disk = disk_new(self.__device)

    @diskDecorator()
    def delete_all(self):
        """
        This method deletes all partitions from disk.

        *Raises:*
            DiskError, DiskCommitError

        .. note::

            If the disk is initialized (no partition table) it
            will return None.
        """
        disk_delete_all(self.__disk)
        return

    @diskDecorator(error=True)
    def commit(self):
        """
        This method commits partition modifications to disk.

        *Raises:*
            DiskError, DiskCommitError

        .. note::

            If the disk is initialized (no partition table) it
            will return None.
        """
        to_dev = disk_commit_to_dev(self.__disk)
        if not to_dev:
            raise DiskCommitError(601)
        to_os = disk_commit_to_os(self.__disk)
        if not to_os:
            raise DiskCommitError(602)

    def _get_ped_partition(self, part_num):
        partition = disk_get_partition(self.__disk, part_num)
        if not bool(partition):
            raise PartitionError(705)
        return partition

    @diskDecorator(error=True)
    def get_partition(self, part_num):
        """
        Returns a Partition instance.

        *Args:*
            part_num (int):     A partition number.

        *Raises:*
            PartitionError

        .. note::

            If the disk is initialized (no partition table) it
            will raise DiskError.
        """
        partition = Partition(part=self._get_ped_partition(part_num))
        return partition

    def _destroy_disk(self, disk=None):
        if disk:
            disk_destroy(disk)
        else:
            if self.__disk:
                disk_destroy(self._ped_disk)
                self.__disk = None
            else:
                raise DiskError(600)

    def set_label(self, label):
        """
        Sets the disk partition table ('gpt' or 'msdos)'.
        This method calls commit to set the label changes.

        *Args:*
            label (str):    A partition table type ('gpt' or 'msdos')

        *Raises:*
            DiskError
        """
        if label not in disk_labels:
            raise DiskError(603)
        disk_type = disk_get_type(label)
        if not bool(disk_type):
            raise DiskError(604)
        if bool(self._ped_disk):
            self._destroy_disk()
        new_disk = disk_new_fresh(self._ped_device, disk_type)
        if not bool(new_disk):
            raise DiskError(605)
        self.__disk = new_disk
        self.commit()
        self._destroy_disk(disk=new_disk)
        self.__disk = disk_new(self.__device)

class Partition(object):
    """
    *Partition class is used as a wrapper to libparted's ped_partition.*

    You need can create Partition instances and add them to disk. A new
    Partition instance can be initialized::

        from reparted import *

        myDevice = Device("/dev/sda")
        myDisk = Disk(myDevice)
        mySize = Size(4, "GB")

        # Defaults
        myPartition = Partition(myDisk, mySize)

        # Different filesystem and minimal alignment.
        myPartition = Partition(myDisk, mySize, fs="ext4", align="minimal")

        # Initialize with a name
        if myDisk.type_features == 'PARTITION_NAME':
            myPartition = Partition(myDisk, mySize, name="test")

    *Args:*
        disk:           A Disk class instance.
        size:           A Size class instance.
        type (str):     The partition type (ie. 'NORMAL', 'LOGICAL', etc...).
        fs (str):       The filesystem type (ie. 'ext3', 'ext4', etc...).
        align (str):    The partition alignment, 'minimal' or 'optimal'.
        name (str):     The partition name.
        start (int):    The start sector for the partition.
        end (int):      The end sector for the partition.
        part:           A ctypes ped_partition pointer.

    *Raises:*
        PartitionError

    .. note::

       Name is only available when partition type is 'NORMAL'.
       The start and end arguments are optional and you should only use them when
       your want to specify such attributes, otherwise use optimal alignment.
       The part argument is optional and mostly for internal use.
    """
    def __init__(self, disk=None, size=None, type='NORMAL', fs='ext3', align='optimal',
                    name='', start=None, end=None, part=None):
        if part:
            self.__align = None
            self.__partition = part
            self.__ped_disk = self.__partition.contents.disk
            self.__disk = Disk(disk=self.__ped_disk)
        elif disk and size:
            self.__align = align
            if not type in partition_type.values():
                raise PartitionError(707)
            part_type = [key for key,val in partition_type.iteritems() if val == type][0]
            if type != 'EXTENDED' and fs != None:
                filesystem = file_system_type_get(fs)
            self.__ped_disk = disk._ped_disk
            self.__disk = Disk(disk=self.__ped_disk)
            if align == 'optimal' or align == 'minimal':
                dev = disk._ped_device
                a_start, a_end = self._get_alignment(dev, align, start, end, size)
            else:
                raise PartitionError(708)
            self.__partition = partition_new(self.__ped_disk, part_type, filesystem, a_start, a_end)
            if name:
                self.set_name(name)
        else:
            raise PartitionError(700)

    @property
    def disk(self):
        """
        Returns the ctypes ped_disk pointer.
        """
        return self.__disk

    @property
    def device(self):
        """
        Returns the Device instance this partition belongs to.
        """
        return self.disk.device

    @property
    def geom(self):
        """
        Returns the partition geometry as a 3-tuple:

            (start, end, length)
        """
        start =  self.__partition.contents.geom.start
        end =  self.__partition.contents.geom.end
        length =  self.__partition.contents.geom.length
        return (start, end, length)

    @property
    def num(self):
        """
        Returns the partition number.
        """
        return self.__partition.contents.num

    @property
    def type(self):
        """
        Returns the partition type.
        """
        return partition_type[self.__partition.contents.type]

    @property
    def fs_type(self):
        """
        Returns the partition filesystem type.
        """
        try:
            fs = self.__partition.contents.fs_type.contents.name
        except ValueError:
            fs = None
        return fs

    @property
    def name(self):
        """
        Returns the partition name if names are supported by disk type,
        otherwise returns None.
        """
        if self.disk.type_features != 'PARTITION_NAME':
            return None
        return partition_get_name(self.__partition)

    @property
    def alignment(self):
        """
        Returns the partition alignment ('optimal' or 'minimal').

        .. note::

            If you specify a 'minimal' alignment when creating a partition
            but the start sector falls in what would be considered an
            optimal alignment this method will return 'optimal'.
        """
        if self.__align:
            return self.__align
        else:
            optimal = device_get_optimum_alignment(self.disk._ped_device)
            minimal = device_get_minimum_alignment(self.disk._ped_device)
            start, e, l = self.geom
            if start % optimal.contents.grain_size == optimal.contents.offset:
                return 'optimal'
            if start % minimal.contents.grain_size == minimal.contents.offset:
                return 'minimal'
        return None

    def set_name(self, name):
        """
        Sets the partition name. If the disk type does not support
        partition names it will raise NotImplementedError.

        *Args:*
            name (str):         The partition name.

        *Raise:*
            NotImplementedError, PartitionError
        """
        if self.disk.type_features != 'PARTITION_NAME':
            raise NotImplementedError("The disk does not support partition names.")
        new_name = partition_set_name(self.__partition, name)
        if not new_name:
            raise PartitionError(704)
        return

    def _snap_sectors(self, start, end, size):
        if start:
            if not end:
                end = start + size.sectors - 1
            if (end - start) != (size.sectors - 1):
                raise PartitionError(709)
        else:
            last_part_num = disk_get_last_partition_num(self.disk._ped_disk)
            last_part = disk_get_partition(self.disk._ped_disk, last_part_num)
            last_end_sector = last_part.contents.geom.end
            start = last_end_sector + 1
            end = start + size.sectors - 1
        return (start, end)

    def _get_alignment(self, dev, align, start, end, size):
        const = getattr(parted, "ped_device_get_%s_aligned_constraint" % align)
        constraint = const(dev)
        start_offset = constraint.contents.start_align.contents.offset
        start_grain = constraint.contents.start_align.contents.grain_size
        end_offset = constraint.contents.end_align.contents.offset
        end_grain = constraint.contents.end_align.contents.grain_size
        snap_start, snap_end = self._snap_sectors(start, end, size)
        if snap_start % start_grain == start_offset:
            start = snap_start
        else:
            start = ((snap_start / start_grain) + 1) * start_grain
        end = start + size.sectors
        if (end - end_offset) % end_grain != end_offset:
            end = ((end / end_grain) * end_grain) + end_offset
        return (start, end)

    def _get_percent_size(self, length):
        device_length = self.device.length
        return

    def _check_flag(self, flag):
        if not flag in partition_flag.keys():
            raise PartitionError(710)
        check = partition_is_flag_available(self.__partition, partition_flag[flag])
        if not check:
            raise PartitionError(710)

    def set_flag(self, flag, state):
        """
        Sets the partition flag (ie. 'BOOT', 'ROOT', etc...).

        *Args:*
            flag (str):         The partition flag.
            state (bool):       Toggle the flag state (True or False).
        """
        self._check_flag(flag)
        partition_set_flag(self.__partition, partition_flag[flag], int(state))