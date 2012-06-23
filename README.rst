Introduction
============

Reparted is my attempt at learning python ctypes module to create bindings for c api's so use it
at your own risk. I was a bit confused on the way parted and pyparted interface works, my aim was
to create a simple interface. It does not have the full set of features parted has to offer, only
enough to create and delete partitions and set the labels. It has been tested using python 2.7 and
libparted 3.0. Feel free to check the code and point out enhancements.
For any questions my email is rq.sysadmin@gmail.com, have fun!


Downloads
=========

You can download the package from PyPi:

    http://pypi.python.org/pypi/reparted/

or checkout reparted on github:

    http://github.com/xzased/reparted


Installation
============

You can get reparted using pip to install it from PyPI::

    pip install -U reparted

.. note::
    You must have libparted installed and available from your LD_LIBRARY_PATH


Documentation
=============

You can view the documentation and quickstart guide here:

    http://xzased.github.com/reparted


1.2 Release Notes
=================

**Changes from 1.1**

There are no syntax changes in this version (and hopefully never will), so code working on
previous versions should work just fine, however, there are some minor structure changes that
improve readability and fixed weird behavior. The Partition class has been moved to its own
module *partition.py*, this will not affect you if you are importing like::

    from reparted import *

Other than that, there are only the following bugfixes and cool additions:

**Bug Fixes**

*       *Failed to add primary partition after extended partition was created in msdos disks.*
*       *Reparted would segfault if attempting to add logical partitions on non-msdos disks.*
*       *Partition types were not being checked against disk types and extended partitions.*


**Additions**

*       *Basic operation support for size class.*
*       *Device, Disk and Partition instances provide a size method.*
*       *Disk class now provides usable_free_space and total_free_space methods.*
*       *Logical partitions are added automatically to extended partitions*
        (you can still provide the start and/or end sector if you want to).*



1.1 Release Notes
=================

**Bug Fixes**

*       *No error was raised when calling Device with an invalid path.*
*       *Calculations in to method from Size class were wrong.*
*       *Reparted would segfault when initializing a fresh disk and call certain disk methods.*


**Additions**

*       *Custom exceptions.*
*       *Nice documentation.*