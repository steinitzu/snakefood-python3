from __future__ import print_function, absolute_import

"""
Various tests.
"""

import snakefood.gendeps
from .testsupport import data, compare_expect
from os.path import join


_files = [
    'simple/stdlib.py',
    'simple/invalid.py',
    'simple/notfound.py',
    'project/foo_import.py',
    'project/foo_from.py',
    'project/sub1/sub11/relative_from.py',
    ]

def test_various():
    "Test ignoring unused imports."

    for fn in _files:
        fn = join(data, fn)
        print('Testing for: %s' % fn)
        compare_expect(fn.replace('.py', '.expect'), None,
                       snakefood.gendeps.main, #'sfood', 
                       fn, filterdir=(data, 'ROOT'))


