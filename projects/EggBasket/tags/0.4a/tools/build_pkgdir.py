#!/usr/bin/env python
"""Sort a directory with Python packages into sub-directories by package name.
"""

import os
import re
import shutil
import sys

from os.path import join, isdir
from eggbasket.util import has_extension
from eggbasket.pkginfo import read_pkg_info

pkgname_rx = re.compile(r'(?P<name>[\w_]+?)-.*')
pkgextensions = ('.egg', '.exe', '.rpm', '.tar', 'tar.bz2', 'tar.gz', 'tar.Z', '.tgz', '.zip')

def main(args):
    try:
        srcdir = args[0]
        dstdir = args[1]
    except IndexError:
        print "Usage: build_pkgdir.py SRCDIR DESTDIR"
        sys.exit(2)
    for filename in os.listdir(srcdir):
        pkgpath = join(srcdir, filename)
        if has_extension(filename, pkgextensions):
            pkginfo = read_pkg_info(pkgpath)
            m = pkgname_rx.match(filename)
            if m:
                pkgbasename = m.group('name')
            if pkginfo:
                pkgname = pkginfo['name']
            elif m:
                pkname = pkgbasename
            else:
                print "Packge not recognised: %s" % filename
                continue

            pkgdir = join(dstdir, pkgname)
            dstpath = join(pkgdir, filename)
            if not isdir(pkgdir):
                os.makedirs(pkgdir)
                print "Copying '%s' to '%s'" % (pkgpath, dstpath)
                shutil.copy(pkgpath, dstpath)
            if pkginfo and m and pkgname != pkgbasename:
                print "Package name differs from package file base name!"
                print "Trying to create a symbolic link"
                try:
                    os.symlink(pkgdir, join(dstdir, pkgbasename))
                except:
                    pass

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
