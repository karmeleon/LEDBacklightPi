#! -*- coding: utf-8 -*-
from collections import Iterator

from .math_ import euclidean


__all__ = 'CMap', 'PQueue',


class CMap(object):

    def __init__(self):
        self.vboxes = []

    @property
    def palette(self):
        return map(lambda d: d['color'], self.vboxes)

    def append(self, item):
        self.vboxes.append({'vbox': item, 'color': item.average})

    def __len__(self):
        return len(self.vboxes)

    def nearest(self, color):
        if not self.vboxes:
            raise Exception('Empty VBoxes!')

        min_d = float('Inf')
        p_color = None
        for vbox in self.vboxes:
            vbox_color = vbox.color
            distance = euclidean(color, vbox_color)
            if min_d > distance:
                min_d = distance
                p_color = vbox.color

        return p_color

    def map(self, color):
        for vbox in self.vboxes:
            if vbox.contains(color):
                return vbox.color

        return self.nearest(color)

def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K

class PQueue(Iterator):

    def __init__(self, sorted_key):
        self.sorted_key = sorted_key
        self.items = []
        self.sorted_ = False

    def __next__(self):
        if not self.sorted_:
            self.items = sorted(self.items, key=cmp_to_key(self.sorted_key))
            self.sorted_ = True

        if not self.items:
            raise StopIteration

        return self.pop()

    def append(self, item):
        items = self.items.append(item)
        self.sorted_ = False

    def pop(self):
        if not self.sorted_:
            self.items = sorted(self.items, key=cmp_to_key(self.sorted_key))
            self.sorted_ = True

        r = self.items[0]
        self.items = self.items[1:]
        return r

    def __len__(self):
        return len(self.items)
