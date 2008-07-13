#!/usr/bin/env python

import os
import sys

from os.path import *

import pkg_resources
pkg_resources.require("TurboGears")

import turbogears

def start():
    """Start the CherryPy application server."""

    import cherrypy
    cherrypy.lowercase_api = True

    from imaptofeed.cachecontrol import ExpiresFilter

    curdir = os.getcwd()

    # first look on the command line for a desired config file,
    # if it's not on the command line, then look for setup.py
    # in the current directory. If it's not there, this script is
    # probably installed and we'll look first for a file called
    # 'prod.cfg' in the current directory and then for a default
    # packaged in the egg.
    if len(sys.argv) > 1:
        turbogears.update_config(configfile=sys.argv[1],
            modulename="imaptofeed.config")
    elif exists(join(curdir, "setup.py")):
        turbogears.update_config(configfile="dev.cfg",
            modulename="imaptofeed.config")
    elif exists(join(curdir, "prod.cfg")):
        turbogears.update_config(configfile="prod.cfg",
            modulename="imaptofeed.config")
    else:
        try:
            configfile = pkg_resources.resource_filename(
                Requirement.parse("Imap2Feed"), "config/default.cfg")
        except pkg_resources.DistributionNotFound:
            print "Could not find default configuration."
            sys.exit(1)

    from imaptofeed.controllers import Root
    root = Root()
    cherrypy.root = root
    turbogears.start_server(root)
