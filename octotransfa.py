#!/usr/bin/env python3

from __future__ import print_function
import os
import subprocess
import uuid

# Change the import directory here to specify the transfer list ...
# and, yes, of course this isn't how you should be doing things. But
# time sensitive matters, no?
from transfer_file_list import transfer_list

# Base path to the three HDD mount point
hdd_path_options = [
    '/path/to/disk1/mount',
    '/path/to/disk2/mount',
    '/path/to/disk3/mount',
]

hdd_path = hdd_path_options[0]
hdd_path_idx = 0
hdd_path_max_idx = len(hdd_path_options) - 1


# Useful functions
def space_of_thost_subdir(path):
    output = subprocess.check_output(
        "ssh thost05 du -s %s" % path,
        shell=True,
    )

    return int(output.split()[0])

def space_left_on_hdd():
    global hdd_path

    output = subprocess.check_output(
        "df %s | tail -1 | awk '{print $4}'" % hdd_path,
        shell=True,
    )

    return int(output.split()[-1])


# Transfer stuff
for idx, transfer_pair in enumerate(transfer_list):
    # Unpack stuff
    source_thost_path, dest_path_suffix = transfer_pair
    dest_path = os.path.join(hdd_path, dest_path_suffix)

    # Check if we have space on the hard disk
    if space_left_on_hdd() < space_of_thost_subdir(source_thost_path):
        # Next HDD!
        if hdd_path_idx < hdd_path_max_idx:
            hdd_path_idx += 1
            hdd_path = hdd_path_options[hdd_path_idx]
        else:
            # No more space :(
            break

    # We have space! Yay!
    subprocess.check_call(
        'rsync -avPL thost:%s %s' % (source_thost_path, dest_path),
        shell=True)

    # See ya!
    del transfer_list[idx]


# Spit back what files remain to be transfered
with open(uuid.uuid4 + '.txt', 'w') as f:
    print(transfer_list, file=f)
