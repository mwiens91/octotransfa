#!/usr/bin/env python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import datetime
import os
import subprocess

# Change the import directory here to specify the transfer list ...
# and, yes, of course this isn't how you should be doing things. But
# time sensitive matters, no?
from transfer_file_list import transfer_list

# ANSI escape for bold
ANSI_BOLD = "\033[1m"
ANSI_END = "\033[0m"

# Host name
SOURCE_HOSTNAME = "source_hostname"

# Base path to the HDD mount points
hdd_path_options = [
    "/path/to/disk1/mount/point",
    "/path/to/disk2/mount/point",
    "/path/to/disk3/mount/point",
]

hdd_path = hdd_path_options[0]
hdd_path_idx = 0
hdd_path_max_idx = len(hdd_path_options) - 1


# Useful functions
def space_of_source_subdir(path):
    """Finds the size of a directory and its children."""
    global SOURCE_HOSTNAME

    output = subprocess.check_output(
        "ssh %s du -s %s" % (SOURCE_HOSTNAME, path), shell=True
    )

    return int(output.split()[0])


def space_left_on_hdd():
    """Finds the size left on the current HDD."""
    global hdd_path

    output = subprocess.check_output(
        "df %s | tail -1 | awk '{print $4}'" % hdd_path, shell=True
    )

    return int(output.split()[-1])


# Keep track of what remains to be transfered
indices_processed = []

# Transfer stuff
for idx, transfer_pair in enumerate(transfer_list):
    # Unpack stuff
    source_path, dest_path_suffix = transfer_pair
    dest_path = os.path.join(hdd_path, dest_path_suffix)

    # Check if we have space on the hard disk
    try:
        if space_left_on_hdd() < space_of_source_subdir(source_path):
            # Next HDD!
            if hdd_path_idx < hdd_path_max_idx:
                # Refresh the current HDD
                hdd_path_idx += 1
                hdd_path = hdd_path_options[hdd_path_idx]

                # Refresh the destination path (so it uses the new HDD)
                dest_path = os.path.join(hdd_path, dest_path_suffix)
            else:
                # No more HDDs
                break

        # We have space! Yay!
        print()
        print(
            ANSI_BOLD
            + "Transfering %s:%s -> %s"
            % (SOURCE_HOSTNAME, source_path, dest_path)
            + ANSI_END
        )
        print()

        # Make sure the parent directories exist on the destination
        subprocess.check_call("mkdir -p %s" % (dest_path), shell=True)

        # Transfer!
        subprocess.check_call(
            "rsync -avPL %s:%s %s" % (SOURCE_HOSTNAME, source_path, dest_path),
            shell=True,
        )
    except Exception as e:
        # Print the exception
        print("An exception occurred!")
        print(e)

        # Exit the loop
        break

    # Mark this as processed
    indices_processed += [idx]


# Spit back what files remain to be transfered

while indices_processed:
    del transfer_list[indices_processed.pop()]

output_file_name = (
    "transfer_file_list_"
    + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    + ".py"
)

with open(output_file_name, "w") as f:
    print("transfer_list = ", end="", file=f)
    print(transfer_list, file=f)
