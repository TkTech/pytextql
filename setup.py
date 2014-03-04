#!/usr/bin/env python
# -*- coding: utf8 -*-
import os.path
from setuptools import setup, find_packages


def get_version():
    """
    Loads the current module version from version.py and returns
    it.

    :returns: module version identifier.
    :rtype: str
    """
    local_results = {}
    version_file_path = os.path.join('pytextql', 'version.py')

    # This is compatible with py3k which removed execfile.
    with open(version_file_path, 'rb') as fin:
        # Compiling instead of passing the text straight to exec
        # associates any errors with the correct file name.
        code = compile(fin.read(), version_file_path, 'exec')
        exec(code, {}, local_results)

    return local_results['__version__']


if __name__ == '__main__':
    setup(
        name='pytextql',
        author='Tyler Kennedy',
        author_email='tk@tkte.ch',
        url='https://github.com/TkTech/pytextql',
        version=get_version(),
        packages=find_packages(),
        include_package_data=True,
        install_requires=[
            'docopt'
        ],
        scripts=[
            'pytextql/pytextql'
        ]
    )
