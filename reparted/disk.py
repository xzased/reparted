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
        def wrapped(self):
            if bool(self._ped_disk):
                return fn(self)
            if error:
                raise DiskError(606)
            return None
        return wrapped
    return wrap

class Disk(object):
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
        return self.__device

    @property
    def _ped_disk(self):
        return self.__disk

    @property
    @diskDecorator()
    def type_name(self):
        return self.__disk.contents.type.contents.name

    @property
    @diskDecorator()
    def device(self):
        return self.__device

    @property
    @diskDecorator()
    def type_features(self):
        feat = self.__disk.contents.type.contents.features
        return disk_features[feat]

    @property
    @diskDecorator()
    def block_sizes(self):
        return self.__disk.contents.block_sizes

    @property
    @diskDecorator()
    def needs_clobber(self):
        return bool(self.__disk.contents.needs_clobber)

    @property
    @diskDecorator()
    def update_mode(self):
        return bool(self.__disk.contents.update_mode)

    @diskDecorator()
    def partitions(self):
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
        disk_delete_all(self.__disk)
        return

    @diskDecorator(error=True)
    def commit(self):
        to_dev = disk_commit_to_dev(self.__disk)
        if not to_dev:
            raise DiskCommitError(601)
        to_os = disk_commit_to_os(self.__disk)
        if not to_os:
            raise DiskCommitError(602)

    @diskDecorator(error=True)
    def _get_ped_partition(self, part_num):
        partition = disk_get_partition(self.__disk, part_num)
        if not bool(partition):
            raise PartitionError(705)
        return partition

    @diskDecorator(error=True)
    def get_partition(self, part_num):
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
        return self.__disk

    @property
    def device(self):
        return self.disk.device

    @property
    def geom(self):
        start =  self.__partition.contents.geom.start
        end =  self.__partition.contents.geom.end
        length =  self.__partition.contents.geom.length
        return (start, end, length)

    @property
    def num(self):
        return self.__partition.contents.num

    @property
    def type(self):
        return partition_type[self.__partition.contents.type]

    @property
    def fs_type(self):
        try:
            fs = self.__partition.contents.fs_type.contents.name
        except ValueError:
            fs = None
        return fs

    @property
    def name(self):
        if self.disk.type_features != 'PARTITION_NAME':
            return None
        return partition_get_name(self.__partition)

    @property
    def alignment(self):
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
        self._check_flag(flag)
        partition_set_flag(self.__partition, partition_flag[flag], int(state))