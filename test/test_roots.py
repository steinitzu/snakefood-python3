from __future__ import print_function, absolute_import

"""
Test roots computation.
"""

import snakefood.gendeps
from .testsupport import data, compare_expect, find_dirs
from os.path import join

def test_roots():
    "Test that the root directories are being calculated correctly."
    for dn in find_dirs(join(data, 'roots')):
        print('Testing roots for: %s' % dn)
        compare_expect(join(dn, '.expect'), None,
                       snakefood.gendeps.main, #'sfood',
                       '--print-roots', dn, filterdir=(data, 'ROOT'))


