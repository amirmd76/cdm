#!/usr/bin/python
import sys

import subprocess

from utils import read_queue, shift_queue, pop_queue

tries = 0
while True:
    queue = read_queue()
    if not queue:
        print("Nothing to do!")
        sys.exit(0)
    else:
        status = subprocess.call(["axel", "-an", "10", queue[0]])
        if status is not 0:
            print("Failed to download {} :(".format(queue[0]))
            tries += 1
            if tries > 30:
                tries = 0
                shift_queue()
        else:
            print("Downloaded {} :)!".format(queue[0]))
            pop_queue()
