Quickstart
================
Here is the guide for the impatient::

    from reparted import *

    # Initialize a device instance, you can provide the path
    myDevice = Device("/dev/sda")

    # Or you can let it probe standard devices, it will default to the first
    # one it finds.
    myDevice = Device()

    # Initialize our disk.
    myDisk = Disk(myDevice)

    # If this is a fresh disk (no partition table set) you can go ahead
    # and set the partition table.
    myDisk.set_label('gpt')
    myDisk.commit()

You can test if your disk is set with a partition table like this::

    if myDisk.type_name is None:
        # No partition table, set one
        myDisk.set_label('gpt')
        mydisk.commit()

    # You can see if your disk has any partitions
    partitions = myDisk.partitions()

You can add partitions, but first you need to set the size::

    # sector size defaults to 512
    mySize1 = Size(4, "GB")

    # manually set the sector size to 1024
    mySize2 = Size(4, "GB", sector_size=1024)

    # get the sector size from the device
    myDevice = Device('/dev/sda')
    mySize = Size(4, "GB", dev=myDevice)

    # You can even set a percentage!
    myDevice = Device('/dev/sda')
    mySize = Size(25, "%", dev=myDevice)

Now that you have your size, you can initialize a new partition and add it to disk::

    myPartition = Partition(myDisk, mySize)
    myDisk.add_partition(myPartition)
    myDisk.commit()

.. note::
    Unless you specify a starting sector for a new partition, reparted will always search
    for the largest free space available and set the beginning of that area as the starting
    sector for new partitions.

Want to fill a new partition with whatever is free on disk? No hay problema::

    freeSize = myDisk.usable_free_space
    myPartition = Partition(myDisk, freeSize)
    myDisk.add_partition(myPartition)
    myDisk.commit()

Now what about ms-dos disks and extended partitions?::

    myDisk.set_label('msdos')
    myDisk.commit()
    freeSize = myDisk.usable_free_space
    myPartition = Partition(myDisk, freeSize, type="EXTENDED")
    myDisk.add_partition(myPartition)
    myDisk.commit()
    logical = Partition(myDisk, Size(8, "GB"), type="LOGICAL")
    myDisk.add_partition(logical)
    myDisk.commit()

You can also delete partitions::

    partition = myDisk.partitions()[0]
    myDisk.delete_partition(partition)

Or just delete them all::

    myDisk.delete_all()


Checkout the module reference for more available options.

.. note::
    You must have libparted installed and available from your LD_LIBRARY_PATH