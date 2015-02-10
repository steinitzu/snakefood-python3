from __future__ import print_function, absolute_import

"""
Support routines for all tests.
"""

import re
import os
from os.path import exists, join, dirname, abspath
import sys
from subprocess import PIPE, Popen
from snakefood.six import StringIO, reraise
import traceback


__all__ = ('data', 'find_dirs', 'run_sfood', 'compare_expect')



def find_hg_root(start=__file__):
    "Find the root of a Mercurial repository."
    pdn, dn = None, start
    while not exists(join(dn, '.hg')) and pdn != dn:
        pdn, dn = dn, dirname(dn)
    return dn

# Root of the mercurial repo.
hgroot = find_hg_root()

# Executables directory and executables.
bindir = join(hgroot, 'bin')

# Root location where the data files are to be found.
data = join(dirname(__file__), 'data')


def find_dirs(startdir):
    "Returns a list of directories under startdir."
    rdirs = [startdir]
    for root, dirs, files in os.walk(abspath(startdir)):
        rdirs.extend(join(root, x) for x in dirs)
    return rdirs


def run_sfood(*args, **kw):
    """
    Run sfood with the given args, and capture and return output.
    If 'filterdir' is provided, remove those strings are replaced in the output.
    """
    filterdir = kw.get('filterdir', None)
    if callable(args[0]):
        sys.argv, oldargv = list(args), sys.argv
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout = mystdout = StringIO()
        sys.stderr = mystderr = StringIO()
        try:
            args[0]() # run main()
        except:
            t, e, tb = sys.exc_info()
        else:
            e = None
        out, log = mystdout.getvalue(), mystderr.getvalue()
        mystdout.close()
        mystderr.close()
        sys.stdout, sys.stderr = old_stdout, old_stderr
        sys.argv = oldargv
        if e:
            traceback.print_exception(t, e, tb)
        
    else:
        cmd = [join(bindir, args[0])] + list(args[1:])
        print('Running cmd:', file=sys.stderr)
        print(' '.join(cmd), file=sys.stderr)
        print('', file=sys.stderr)
        p = Popen(cmd, shell=False, stdout=PIPE, stderr=PIPE)
        out, log = p.communicate()
        
        if p.returncode != 0:
            print("Program failed to run: %s" % p.returncode, file=sys.stderr)
            print(' '.join(cmd), file=sys.stderr)
        
    if filterdir is not None:
        from_, to_ = filterdir
        out = re.sub(re.escape(from_), to_, out)
        log = re.sub(re.escape(from_), to_, log)

    return out, log



def compare_expect(exp_stdout, exp_stderr, *args, **kw):
    out, err = run_sfood(*args, **kw)
    print('stdout:\n',out)
    print('stderr:\n',err)

    filterdir = kw.get('filterdir', None)

    for name, efn, text in (('stdout', exp_stdout, out),
                            ('stderr', exp_stderr, err)):
        if efn is None:
            continue
        expected = open(efn).read()
        if filterdir is not None:
            from_, to_ = filterdir
            expected = re.sub(re.escape(from_), to_, expected)

        try:
            text = text.replace(os.sep, '/')
            assert text == expected, ("Unexpected text: \n%s\n != \n%s\n" % (text, expected))
        except AssertionError:
            print("%s:" % name, file=sys.stderr)
            print("--------", file=sys.stderr)
            sys.stderr.write(text)
            print("--------", file=sys.stderr)
            print("", file=sys.stderr)
            print("expected:", file=sys.stderr)
            print("--------", file=sys.stderr)
            sys.stderr.write(expected)
            print("--------", file=sys.stderr)
            raise

