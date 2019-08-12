#!/usr/bin/python
import argparse
import os
import sys

import subprocess
import time

from cdm.utils import read_queue, shift_queue, pop_queue, get_file_name, file_name_index, read_db, write_queue
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
parser_add.add_argument('-a', '--all', help='add all links', action='store_true', dest='all')
parser_add.add_argument('-u', '--url', type=str, help='url', dest='url')
parser_add.add_argument('-n', '--name', type=str, help='file name', dest='name')

parser_add = subparsers.add_parser('clear', help='clear queue')

args = parser.parse_args()


def start(args, db):
    print("Starting ...")

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
        db = read_db()
        queue = read_queue(db)
        if not queue:
            print("Nothing to do!")
            if args.watch:
                time.sleep(5)
                continue
            return 0
        url = queue[0]
        name = None
        if isinstance(url, dict):
            name = url.get('name')
            url = url['url']
        db.setdefault('urls', {}).setdefault(url, {'state': 'p'})
        if db['urls'][url]['state'] == 'f' and not args.ndu:
            pop_queue()
            continue

        fnd = True
        should_continue = False
        idx = 0
        name = get_file_name(url)
        file_name = name
        while fnd:
            file_name = file_name_index(name, idx)
            fnd = os.path.exists(file_name)
            if fnd:
                if args.ndf:
                    print("Duplicate file {}, ignoring".format(file_name))
                    pop_queue()
                    should_continue = True
                    break
                idx += 1

        if should_continue:
            continue

        db['urls'][url]['state'] = 'r'
        print('Starting to download {}'.format(file_name))
        path = os.path.join(folder, file_name)
        if os.path.isdir(path) and name:
            path = os.path.join(path, name)
        status = subprocess.call("axel -an 10 \"{}\" --max-redirect=1000 -o \"{}\"".
                                 format(url, path),
                                 shell=True)
        if status is not 0:
            db['urls'][url]['state'] = 'w'
            db['urls'][url].setdefault('tries', 0)
            db['urls'][url]['tries'] += 1
            if db['urls'][url]['tries'] > 30 and not args.ndrop:
                pop_queue()
                continue
            print("Failed to download {} :(".format(queue[0]))
            tries += 1
            time.sleep(3)
            if tries > 10:
                tries = 0
                shift_queue()
        else:
            db['urls'][url]['state'] = 'f'
            print("Downloaded {} :)!".format(queue[0]))
            pop_queue()
    return 0


def main():
    try:
        status = 0
        db = read_db()
        if args.command == 'start':
            status = start(args, db)
        elif args.command == 'add':
            status = add(args, db)
        elif args.command == 'clear':
            write_queue(db, [])
    except KeyboardInterrupt:
        print("Exited")
        sys.exit(3)


main()
