#!/usr/bin/env python
"""FIXME: Enter file docstring here."""

import os, sys

from optparse import OptionParser

def parse_toplevel(project_dir):
    """Parse top_level.txt file in the project.egg-info directory.

    Returns list of top-level package names."""

    project_name = dirname(project_dir)
    try:
        fo = open(join(project_dir, '%s.egg-info'  % project_name))
    except:
        return None
    else:
        packages = [line.strip for line in fo.readlines if line.strip()]
        fo.close()
        return packages


def main(args):
    global options, optparser

    optparser = OptionParser(prog=__program__, usage=__usage__,
      version=__version__, description=__doc__)
    optparser.add_option("-v", "--verbose",
      action="store_true", dest="verbose", default=False,
      help="Print what's going on to stdout.")
    optparser.add_option("-h", "--host",
      action="store", dest="host",
      help="Hostname of deployment server")
    optparser.add_option("-d", "--dest-dir",
      action="store", dest="dest_dir",
      help="Destination directory on deployment server "
        "(project name will be appended).")

    (options, args) = optparser.parse_args(args=args)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
