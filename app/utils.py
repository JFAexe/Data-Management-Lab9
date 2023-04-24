import datetime
from random import random


def time_now():
    return datetime.datetime.now().isoformat(timespec='seconds')


def get_nanoid(size=16):
    alphabet = 'useandom-26T198340PX75pxJACKVERYMINDBUSHWOLF_GQZbfghjklqvwyzrict'
    return ''.join([alphabet[int(random() * 64) | 0] for _ in range(size)])
