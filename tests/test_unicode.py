# -*- coding: utf-8 -*-
import os.path
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import nose.tools as tools

from pytextql import util


def test_unicode_utf8_read():
    """
    Ensure that we can read a unicode file without raising an
    encoding exception.
    """
    sample_path = os.path.join('tests', 'sample_small_unicode.csv')

    with open(sample_path, 'rU') as sample_io:
        reader = util.UnicodeCSVReader(sample_io)

        for row in reader:
            pass


@tools.raises(UnicodeDecodeError)
def test_unicode_ascii_read_fail():
    """
    Ensure that our unicode test file would actually raise an
    exception if encoding was not provided.
    """
    sample_path = os.path.join('tests', 'sample_small_unicode.csv')

    with open(sample_path, 'rU') as sample_io:
        reader = util.UnicodeCSVReader(
            sample_io,
            encoding='ascii'
        )

        for row in reader:
            pass


def test_unicode_utf8_read_write():
    """
    Ensure that we can read and write out a unicode file without
    raising an encoding exception.
    """
    sample_path = os.path.join('tests', 'sample_small_unicode.csv')
    csv_buffer = StringIO()

    with open(sample_path, 'rU') as sample_io:
        reader = util.UnicodeCSVReader(sample_io)
        writer = util.UnicodeCSVWriter(csv_buffer)

        for row in reader:
            writer.writerow(row)

    csv_buffer.close()
