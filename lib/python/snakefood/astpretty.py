from __future__ import print_function, absolute_import

"""Python AST pretty-printer.

This module exports a function that can be used to print a human-readable
version of the AST.
"""
# This file is part of the Snakefood open source package.
# See http://furius.ca/snakefood/ for licensing details.

import ast
import traceback

def main():
    import optparse
    parser = optparse.OptionParser(__doc__.strip())
    opts, args = parser.parse_args()

    if not args:
        parser.error("You need to specify the name of Python files to print out.")


    for fn in args:
        print('\n\n%s:\n' % fn)
        with open(fn) as fp:
            try:
                print(ast.dump(ast.parse(fp.read())))
            except SyntaxError:
                traceback.print_exc()

if __name__ == '__main__':
    main()


