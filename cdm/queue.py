#!/usr/bin/python

from cdm.utils import parse_urls, validate_url, add_to_queue


def add(args, db):
    if args.file:
        if not args.file:
            print('file not specified')
            return 1
        file = open(args.file, 'r+')
        content = file.read()
        file.close()
        parse_urls(db, content)
    else:
        if not args.url:
            print('no url specified')
            return 1
        url = args.url
        if not validate_url(url):
            print('invalid url')
            return 1
        add_to_queue(db, url)
