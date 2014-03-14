# -*- coding: utf-8 -*-
import os
import os.path
import sqlite3
import tempfile

import nose.tools as tools

from pytextql import core


@tools.raises(core.TableExists)
def test_overwrite_none():
    """
    Ensure an error is raised if the table already exists in the
    given database.
    """
    try:
        __, tmp_path = tempfile.mkstemp()

        with core._open_db(db_path=tmp_path) as db:
            db.row_factory = sqlite3.Row

            core._create_table(
                db,
                'tbl1',
                ['test', 'test_two']
            )

        with core._open_db(db_path=tmp_path) as db:
            db.row_factory = sqlite3.Row

            core._create_table(
                db,
                'tbl1',
                ['test', 'test_two']
            )
    finally:
        os.remove(tmp_path)


def test_overwrite_success():
    """
    Ensure that no error is raised if the table already exists in
    the given database if overwrite is ``True``.
    """
    try:
        __, tmp_path = tempfile.mkstemp()

        with core._open_db(db_path=tmp_path) as db:
            db.row_factory = sqlite3.Row

            core._create_table(
                db,
                'tbl1',
                ['test', 'test_two']
            )

        with core._open_db(db_path=tmp_path) as db:
            db.row_factory = sqlite3.Row

            core._create_table(
                db,
                'tbl1',
                ['test', 'test_two'],
                overwrite=True
            )
    finally:
        os.remove(tmp_path)
