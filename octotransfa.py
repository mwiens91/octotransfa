#!/usr/bin/env python3

import subprocess

# Change the import directory here to specify the transfer list ...
# and, yes, of course this isn't how you should be doing things. But
# time sensitive matters, no?
from transfer_file_list import transfer_list

# Base path to HDD mount point
hdd_path = '/home/matt/temp'


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
