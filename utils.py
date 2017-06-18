import os
from urlparse import urlparse

from ftypes import allowed_types


def get_db():
    slf = os.path.abspath(__file__)
    dir = os.path.dirname(slf)
    return os.path.join(dir, 'db')


def remove_empty(x):
    return filter(lambda a: a != '', x)


def get_extention(x):
    if not x:
        return "fuck"
    if x[-1] == '.':
        return "fuck"
    lis = x.split('.')
    return lis[-1].upper()


def validate_url(url):
    if not urlparse(url).hostname:
        return False
    return get_extention(urlparse(url).path) in allowed_types


def read_queue():
    with open(get_db(), 'r+') as file:
        queue = file.read().split()
    queue = remove_empty(queue)
    return queue


def write_queue(queue):
    with open(get_db(), 'w+') as file:
        for q in queue:
            file.write(q)
            file.write('\n')


def add_to_queue(url):
    print(url + " added to queue")
    queue = read_queue()
    if url not in queue:
        queue.append(url)
    write_queue(queue)


def shift_queue():
    print("queue shifted")
    queue = read_queue()
    if len(queue) > 0:
        element = queue.pop(0)
        queue.append(element)
    write_queue(queue)


def pop_queue():
    print("queue popped")
    queue = read_queue()
    if len(queue) > 0:
        queue.pop(0)
    write_queue(queue)


def parse_urls(text):
    inv = "\'\""
    l = text.split()
    for c in inv:
        cpy = []
        for a in l:
            cpy += a.split(c)
        l = cpy
    l = remove_empty(l)
    for s in l:
        if validate_url(s):
            add_to_queue(s)
