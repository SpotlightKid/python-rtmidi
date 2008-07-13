#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys

from genshi.template import TextTemplate

substitutions = dict()
execfile('eggbasket/release.py', substitutions)

def usage():
    print "Usage: make_readme.py INFILE OUTFILE"

def unescape(s):
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    s = s.replace("&quot;", '"')
    s = s.replace("&amp;", "&") # Must be done last!
    return s

def main(args):
    try:
        infile = args[0]
    except IndexError:
        usage()
        sys.exit(2)

    tmpl = TextTemplate(open(infile).read())
    stream = tmpl.generate(**substitutions)

    try:
        out = open(args[1], 'wb')
    except IndexError:
        usage()
    except (IOError, OSError), exc:
        print "Could not open output file %s: %s" % (args[1], exc)
    else:
        out.write(unescape(stream.render(strip_whitespace=False)))
        out.close()

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
