# pytextql

A python-based clone of the textql tool.

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

## Testing

Tests are run using [nose][].

```
pip install nose
python setup.py nosetests
```

### Sample Data

Sample data is generated using [FNG][] and is available as `tests/sample_*.csv`.

[nose]: http://nose.readthedocs.org
[FNG]: http://www.fakenamegenerator.com/