#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""pytextql

A python-based clone of the textql tool.

Usage:
    pytextql [--source <source>...] [-s <query>] [options]
    pytextql columns [--source <source>]

Options:
    --source=<path>     The source file(s) to load, or '-' for STDIN. You
                        can specify any number of sources.
    --no-header         The source files do not contain headers in the first
                        row.
    --named-tables      Use the filenames (without extension) of source files
                        as the table name.
    --db=<path>         Store the resulting SQLite3 database at <path>
                        instead of using a temporary file. A good idea if
                        working on large (100mb+) files.
    --delimiter=<,>     The delimiter used by the source file(s).
                        [default: ,]
    --encoding=<utf8>   The file encoding. If you're getting unicode errors
                        on a file exported from excel, try "cp1250".
                        [default: utf8]
    --chunk-size=<n>    The number of rows to insert per SQLite3 transaction.
                        [default: 50000]
    --sql=<q>, -s       Run an SQL query against the database.
    --skip=<n>          Skip <n> number of rows from the start of the file.
                        [default: 0]
    --overwrite, -o     If a table already exists in a stored database,
                        overwrite it. This is most useful when using
                        named tables.
"""
import os
import sys
import sqlite3
import os.path
import tempfile
import itertools
import contextlib

from docopt import docopt

from pytextql import version, util


class TableExists(Exception):
    pass


@contextlib.contextmanager
def _open_db(db_path=None):
    if db_path:
        full_path = os.path.abspath(
            # ~ may not be expanded when being called from another
            # process instead of a shell.
            os.path.expanduser(db_path)
        )

        conn = sqlite3.connect(full_path)
        with contextlib.closing(conn):
            yield conn
    else:
        __, path = tempfile.mkstemp(suffix='.db', prefix='ptql')

        conn = sqlite3.connect(path)
        with contextlib.closing(conn):
            yield conn

        os.remove(path)


def _source(source, header=True, delimiter=',', encoding='utf8', skip=0):
    reader = util.UnicodeCSVReader(
        source,
        delimiter=delimiter,
        encoding=encoding
    )

    for __ in itertools.repeat(None, skip):
        next(reader)

    # We need the first row, either because it contains the column
    # headers, or because we need to know how many columns there
    # are.
    first_row = next(reader)

    if header:
        headers = [c.strip().lower() for c in first_row]
        # Some CSV exporters do not include empty trailing columns
        # when headers are defined, so we pad and fill them with
        # blank strings by default.
        reader.pad_to = len(headers)
        reader.pad_with = ''
        iterable = reader
    else:
        headers = [u'c{0}'.format(i) for i in xrange(len(first_row))]
        iterable = itertools.chain([first_row], reader)

    return headers, iterable


def _create_table(db, table_name, columns, overwrite=False):
    """
    Create's `table_name` in `db` if it does not already exist,
    and adds any missing columns.

    :param db: An active SQLite3 Connection.
    :param table_name: The (unicode) name of the table to setup.
    :param columns: An iterable of column names to ensure exist.
    :param overwrite: If ``True`` and the table already exists,
                      overwrite it.
    """
    with contextlib.closing(db.cursor()) as c:
        table_exists = c.execute((
            u'SELECT EXISTS(SELECT 1 FROM sqlite_master'
            u' WHERE type="table" and name=?) as "exists"'
        ), (table_name,)).fetchone()

        if table_exists['exists']:
            if not overwrite:
                raise TableExists()

            c.execute(u'DROP TABLE IF EXISTS "{table_name}"'.format(
                table_name=table_name
            ))

        # Create the table if it doesn't already exist.
        c.execute((
            u'CREATE TABLE IF NOT EXISTS "{table_name}"'
            u'(id INTEGER PRIMARY KEY AUTOINCREMENT);'
        ).format(table_name=table_name))

        # Cache the columns that are already there so we create only
        # those that are missing.
        c.execute(u'PRAGMA table_info("{table_name}");'.format(
            table_name=table_name
        ))

        results = c.fetchall()
        existing_columns = set(r['name'] for r in results)

        for header in columns:
            if header in existing_columns:
                continue

            # In SQLite3, new columns can only be appended.
            c.execute((
                u'ALTER TABLE "{table_name}"'
                u' ADD COLUMN "{col}" TEXT;'
            ).format(
                table_name=table_name,
                col=header
            ))

        # Typically, table modifications occur outside of a
        # transaction so this is just a precaution.
        db.commit()


def _load_table(db, table_name, columns, reader, n=50000):
    with contextlib.closing(db.cursor()) as c:
        c.execute(u'PRAGMA synchronous = 0;')
        c.execute(u'PRAGMA journal_mode = MEMORY;')
        c.execute(u'PRAGMA temp_store = MEMORY;')

        query = u'INSERT INTO "{table_name}" values (NULL, {params})'.format(
            table_name=table_name,
            params=u', '.join(u'?' * len(columns))
        )

        for chunk in util.grouper(reader, n):
            c.executemany(query, chunk)

        db.commit()


def main():
    args = docopt(__doc__, version=version.__version__)

    with _open_db(args['--db']) as db:
        db.row_factory = sqlite3.Row

        for table_count, source_path in enumerate(args['--source']):
            # There's at least one file/STDIN to load into the
            # database.
            if source_path == '-':
                # '-' is a placeholder for STDIN.
                source_io = sys.stdin
                table_name = '-'
            elif args['--named-tables']:
                source_io = open(source_path, 'rU')
                # Get the filename (without any extension) and use
                # it as the table's name.
                # FIXME: Normalization?
                table_name = os.path.splitext(
                    os.path.basename(source_path)
                )[0]
            else:
                source_io = open(source_path, 'rU')
                table_name = 'tbl{table_count}'.format(
                    table_count=table_count
                )

            with contextlib.closing(source_io):
                # How many rows should we skip from the start
                # of the file?
                skip_count = max(0, int(args['--skip']))

                headers, reader = _source(
                    source_io,
                    header=(not args['--no-header']),
                    encoding=args['--encoding'],
                    delimiter=args['--delimiter'],
                    skip=skip_count
                )

                if args['columns']:
                    # We just want to print out the column names that
                    # we would end up using, we don't actually want to
                    # load a full table.
                    print(','.join(headers))
                    continue

                _create_table(
                    db,
                    table_name,
                    headers,
                    overwrite=args['--overwrite']
                )

                _load_table(
                    db,
                    table_name,
                    headers,
                    reader,
                    n=int(args['--chunk-size'])
                )

        if args['--sql']:
            with contextlib.closing(db.cursor()) as c:
                c.execute(args['--sql'])
                headers = [d[0] for d in c.description]

                writer = util.UnicodeCSVWriter(
                    sys.stdout,
                    encoding=args['--encoding']
                )
                writer.writerow(headers)

                while True:
                    results = c.fetchmany()
                    if not results:
                        break

                    writer.writerows(list(r) for r in results)


if __name__ == '__main__':
    sys.exit(main())
