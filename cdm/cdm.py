#!/usr/bin/python
import argparse
import os
import sys

import subprocess
import time

from cdm.utils import read_queue, shift_queue, pop_queue, get_file_name, file_name_index, read_db
from cdm.queue import add


parser = argparse.ArgumentParser(prog="cdm", description='Charzeh Download manager')
subparsers = parser.add_subparsers(help='sub-command help', dest="command")
subparsers.required = True

parser_start = subparsers.add_parser('start', help='start downloading')
parser_start.add_argument('-o', '--output', type=str, help='output folder', dest='output')
parser_start.add_argument('-w', '--watch', help='watch for new links', action='store_true', dest='watch')
parser_start.add_argument('-n', '--no_duplicate', help='don\'t download files with the same name', action='store_true',
                          dest='ndf')
parser_start.add_argument('-m', '--no_duplicate_url', help='don\'t download files with the same url',
                          action='store_true', dest='ndu')
parser_start.add_argument('-p', '--no_drops', help='don\'t drop failed downloads',
                          action='store_true', dest='ndrop')


parser_add = subparsers.add_parser('add', help='add to queue')
parser_add.add_argument('-f', '--file', type=str, help='file path to get links from', dest='file')
parser_add.add_argument('-u', '--url', type=str, help='url', dest='url')


args = parser.parse_args()


def start(args, db):
    folder = '.'
    if args.output:
        folder = args.output
    folder = os.path.abspath(folder)
    if os.path.exists(folder):
        try:
            subprocess.call(['mkdir', '-p', folder])
        except:
            print("Can't make directory {}".format(folder))
            return 1

    tries = 0
    while True:
        queue = read_queue(db)
        if not queue:
            if args.watch:
                time.sleep(5)
                continue
            print("Nothing to do!")
            sys.exit(0)
        url = queue[0]
        db.setdefault('urls', {}).setdefault(url, {'state': 'p'})
        if db['urls'][url]['state'] == 'f' and not args.ndu:
            pop_queue(db)
            continue

        fnd = True
        should_continue = False
        idx = 0
        name = get_file_name(url)
        file_name = name
        while fnd:
            file_name = file_name_index(name, idx)
            if os.path.exists(file_name):
                if args.ndf:
                    print("Duplicate file {}, ignoring".format(file_name))
                    pop_queue(db)
                    fnd = False
                    should_continue = True
                    break
                idx += 1
        if should_continue:
            continue
        db['urls'][url]['state'] = 'r'
        status = subprocess.call(["axel", "-an", "10", queue[0], '-o', os.path.join(folder, file_name)])
        if status is not 0:
            db['urls'][url]['state'] = 'w'
            db['urls'][url].setdefalt('tries', 0)
            db['urls'][url]['tries'] += 1
            if db['urls'][url]['tries'] > 30 and not args.ndrop:
                pop_queue(db)
                continue
            print("Failed to download {} :(".format(queue[0]))
            tries += 1
            time.sleep(3)
            if tries > 10:
                tries = 0
                shift_queue(db)
        else:
            db['urls'][url]['state'] = 'f'
            print("Downloaded {} :)!".format(queue[0]))
            pop_queue(db)


def main():
    db = read_db()
    if args.command == 'start':
        start(args, db)
    elif args.command == 'add':
        add(args, db)


main()