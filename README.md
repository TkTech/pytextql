# pytextql

A python-based clone of the textql tool.

## Installing

    pip install pytextql

## Usage

    pytextql [--source <source>...] [-s <query>] [options]

## Options

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

## Examples

Lets play with one of the samples included with the pytextql source. By default,
pytextql treats all data as UTF-8, but you can specify the encoding with
`--encoding=` if you have somethinge exotic.

    pytextql --source tests/sample_small_unicode.csv -s "SELECT DISTINCT(Gender), COUNT(Gender) FROM tbl0 GROUP BY Gender"
    city,COUNT(City)
    Halifax,1
    Val Brillant,1
    Vancouver,1
    Zenon Park,1
    ΑΓΙΟΣ ΓΕΩΡΓΙΟΣ ΚΕΛΟΚΕ∆ΑΡΩΝ,1
    ΑΓΙΟΣ ΕΠΙΦΑΝΕΙΟΣ ΣΟΛΕΑΣ,1
    ΛΑΡΝΑΚΑ,1
    ΠΟΜΟΣ,1
    ΤΑΛΑ,1
    ∆ΙΚΩΜΟ ΚΑΤΩ,1

If you're working with extremely large source files (hundreds of thousands to
millions of rows), you can use the `--db=<path>` option to store the results
and use them over and over again.

    pytextql --source my_really_large_file.csv --db=testing.db
    pytextql --db=testing.db -s "SELECT * FROM tbl0 LIMIT 1"
    ...
    pytextql --db=testing.db -s "SELECT COUNT(id) FROM tbl0;"
    ...

By default, pytextql will error if you attempt to overwrite an existing table. You can use `--overwrite` to overwrite a table if it already exists.

    pytextql -n --named-tables --source filename.csv -s 'select field from filename limit 1' --encoding cp1250 --db=testing.db --overwrite

## Testing

Tests are run using [nose][].

    pip install nose
    python setup.py nosetests

### Sample Data

Sample data is generated using [FNG][] and is available as `tests/sample_*.csv`.

[nose]: http://nose.readthedocs.org
[FNG]: http://www.fakenamegenerator.com/
