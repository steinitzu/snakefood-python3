from __future__ import print_function, absolute_import

"""
A helper module to build simple filter scripts.
"""

import sys
import optparse

def do_filter(populate_parser=None):
    parser = optparse.OptionParser(__doc__.strip())
    opts, args = parser.parse_args()

    if not args:
        args = ['-']
    for fn in args:
        if fn == '-':
            f = sys.stdin
        else:
            f = open(fn)

        for line in f.xreadlines():
            yield eval(line)
