from __future__ import print_function, absolute_import

"""
Functional test for Python checker.
"""

import os
import ast
from os.path import join
from .testsupport import data, compare_expect

from snakefood.find import ImportVisitor
from snakefood.local import NamesVisitor
import snakefood.checker


def visit_source(source, cls):
    mod = ast.parse(source)
    vis = cls()
    vis.visit(mod)
    return vis.finalize()

_import_tests = (
    ('import mymod', ['mymod']),
    ('import mod1, mod2, mod3', ['mod1', 'mod2','mod3']),
    ('import mod1 as mymod', ['mymod']),
    ('import mod1 as mymod, mod2 as mymod2', ['mymod', 'mymod2']),
    ('from mod1 import mymod', ['mymod']),
    ('from mod1 import mymod, mymod2', ['mymod', 'mymod2']),
    ('from mod1 import mymod as bli1', ['bli1']),
    ('from mod1 import mymod as bli1, mymod2 as bli2', ['bli1', 'bli2']),
    ('import os.path', ['os.path']),
    )

_names_tests = [
    ('fn = os.path.join("a", "b")', ['os', 'os.path', 'os.path.join']),
    ]
if snakefood.six.PY2:
    _names_tests.append(
        ('a = 1; print b.c ; d.e = 3', ['b', 'b.c', 'd']) # FIXME why not also d.e?
    )
else:
    _names_tests.append(
        ('a = 1; print(b.c) ; d.e = 3', ['b', 'b.c', 'd'])
    )

def test_checker_functional():
    for source, expected in _import_tests:
        found = visit_source(source, ImportVisitor)
        actual = [x[2] for x in found if x[2] is not None]
        assert actual == expected, (actual, expected)

    for source, expected in _names_tests:
        dotted, simple = visit_source(source, NamesVisitor)
        actual = [x[0] for x in dotted]
        assert actual == expected, (actual, expected)




def test_checker_expected():
    checkdir = join(data, 'checker')
    pytocheck = [join(checkdir, fn) for fn in 
                 os.listdir(checkdir) if fn.endswith('.py')]

    for fn in pytocheck:
        print('Testing checker on: %s' % fn)
        compare_expect(None, fn.replace('.py', '.expect'),
                       snakefood.checker.main, #'sfood-checker', 
                       fn, filterdir=(data, 'ROOT'))

