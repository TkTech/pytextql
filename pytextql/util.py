# -*- coding: utf-8 -*-
import csv
import itertools


def grouper(iterable, n):
    """
    Slice up `iterable` into iterables of `n` items.

    :param iterable: Iterable to splice.
    :param n: Number of items per slice.
    :returns: iterable of iterables
    """
    it = iter(iterable)
    while True:
        chunk = itertools.islice(it, n)
        try:
            first = next(chunk)
        except StopIteration:
            return

        yield itertools.chain([first], chunk)


class UnicodeCSVReader(object):
    """
    An extremely minimal wrapper around csv.reader to assist in
    reading Unicode data.
    """
    def __init__(self, *args, **kwargs):
        self.encoding = kwargs.pop('encoding', 'utf8')
        self.pad_to = kwargs.pop('pad_to', 0)
        self.pad_with = kwargs.pop('pad_with', '')
        self.reader = csv.reader(*args, **kwargs)

    def next(self):
        row = self.reader.next()
        padding = [self.pad_with] * (self.pad_to - len(row))
        return [unicode(c, self.encoding) for c in row] + padding

    def __iter__(self):
        return self

    @property
    def dialect(self):
        return self.reader.dialect

    @property
    def line_num(self):
        return self.reader.line_num


class UnicodeCSVWriter(object):
    def __init__(self, *args, **kwargs):
        self.encoding = kwargs.pop('encoding', 'utf8')
        self.writer = csv.writer(*args, **kwargs)

    def writerow(self, row):
        self.writer.writerow([
            column.encode(self.encoding) for column in row
        ])

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
