#!/usr/bin/env python
"""Looks for changes in Cheetah templates in DIR every INTERVAL seconds and recompiles them when neccessary.

Default check interval is 1 second.
"""

import glob
import os
import sys
import time
from os.path import exists, isfile, join, getmtime, splitext

from Cheetah.CheetahWrapper import CheetahWrapper

__program__   = "cheetah_autocompile"
__author__    = "Christopher Arndt"
__revision__  = "$Rev$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2007 Axandra GmbH"


SRC_EXT = '.tmpl'
DST_EXT = '.py'

def compile(template):
    CheetahWrapper().main(['cheetah-compile', 'compile', template])

def check_dir(directory, src_ext='.tmpl', dst_ext='.py'):
    changed = []
    for dirpath, dirs, files in os.walk(directory):
        for file in files:
            path = join(dirpath, file)
            basename, ext = splitext(file)
            if isfile(path) and ext == src_ext:
                compiled = join(dirpath, basename + dst_ext)
                mtime = getmtime(path)
                if not exists(compiled) or mtime > getmtime(compiled):
                    yield path, mtime

def main(args):
    try:
        workdir = args.pop(0)
    except IndexError:
        print >>sys.stderr, "Usage: cheetah-autocompile DIR [INTERVAL]"
        print >>sys.stderr, __doc__
        return 1
    try:
        checkinterval = int(args.pop(0))
    except (IndexError, ValueError):
        checkinterval = 1

    failed = dict()
    try:
        while True:
            for template, mtime in check_dir(workdir, SRC_EXT, DST_EXT):
                # don't try to compile templates that failed last time
                # and haven't changed
                if mtime <= failed.get(template, 0):
                    continue
                try:
                    compile(template)
                except Exception, exc:
                    print >>sys.stderr, \
                      "Warning: compilation of '%s' failed." % template
                    print >>sys.stderr, exc
                    # compilation failed, put into list of failed templates
                    failed[template] = mtime
                else:
                    # compilation ok, remove from list of failed templates
                    try: del failed[template]
                    except: pass
            if checkinterval == 0:
                break
            time.sleep(checkinterval)
    except KeyboardInterrupt:
        return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
