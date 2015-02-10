from __future__ import print_function, absolute_import

"""
Read a snakefood dependencies file and output the list of all files.
"""
# This file is part of the Snakefood open source package.
# See http://furius.ca/snakefood/ for licensing details.

import sys
from os.path import join
import optparse

from snakefood.depends import read_depends, flatten_depends

def main():
    parser = optparse.OptionParser(__doc__.strip())
    opts, args = parser.parse_args()

    depends = read_depends(sys.stdin)
    for droot, drel in flatten_depends(depends):
        print(join(droot, drel))

