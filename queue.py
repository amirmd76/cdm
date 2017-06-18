#!/usr/bin/python

import sys

from utils import parse_urls, validate_url, add_to_queue

if len(sys.argv) > 1 and sys.argv[1] == '-f':
    if len(sys.argv) == 2:
        raise Exception('file not specified')
    file = open(sys.argv[2], 'r+')
    content = file.read()
    file.close()
    parse_urls(content)

else:
    if len(sys.argv) == 1:
        raise Exception('no url specified')
    url = sys.argv[1]
    if not validate_url(url):
        raise Exception('invalid url')
    add_to_queue(url)
