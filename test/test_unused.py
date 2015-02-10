from __future__ import print_function, absolute_import

"""
Test ignoring unused imports.
"""

import snakefood.gendeps
from .testsupport import data, compare_expect
from os.path import join


_files = ['simple/unused.py']

def test_ignore_unused():
    "Test ignoring unused imports."

    for fn in _files:
        fn = join(data, fn)
        print('Testing ignore unused for: %s' % fn)
        compare_expect(fn.replace('.py', '.expect'), None,
                       snakefood.gendeps.main, #'sfood', 
                       '--ignore-unused', fn, filterdir=(data, 'ROOT'))


