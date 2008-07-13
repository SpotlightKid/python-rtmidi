# -*- coding: utf-8 -*-
"""This module contains functions called from console script entry points."""

import logging
import optparse
import sys

from os import getcwd
from os.path import dirname, exists, join

import pkg_resources
pkg_resources.require("TurboGears >= 1.0.4.4")
pkg_resources.require("SQLAlchemy >= 0.4")
pkg_resources.require("Genshi >= 0.4")
pkg_resources.require("docutils >= 0.4")

import cherrypy
import turbogears

from turbogears.util import load_project_config, get_model


cherrypy.lowercase_api = True
log = logging.getLogger("eggbasket")


class ConfigurationError(Exception):
    pass

def find_config(args):
    """Return for environment-specific configuration in several places.

    First look on the command line for a desired config file,
    if it's not on the command line, then look for 'setup.py'
    in the current directory. If there, load configuration
    from a file called 'dev.cfg'. If it's not there, the project
    is probably installed and we'll look first for a file called
    'prod.cfg' in the current directory and then for a default
    config file called 'default.cfg' packaged in the egg.

    If all fails, raise ConfigurationError.
    """
    setupdir = dirname(dirname(__file__))
    curdir = getcwd()

    if args:
        configfile = args[0]
    elif exists(join(setupdir, "setup.py")):
        configfile = join(setupdir, "dev.cfg")
    elif exists(join(curdir, "prod.cfg")):
        configfile = join(curdir, "prod.cfg")
    else:
        try:
            configfile = pkg_resources.resource_filename(
              pkg_resources.Requirement.parse("EggBasket"),
                "config/default.cfg")
        except pkg_resources.DistributionNotFound:
            raise ConfigurationError("Could not find default configuration.")
    log.info("Using configuration file %s", configfile)
    return configfile

def init_database(args):
    """Create bootstrap data in the database specified by the given config file.

    This will create a user with user_name/password "admin", who belongs
    to the group "maintainers", which has the "upload" permission.

    This function can safely be run several times for the same database. If a
    a user with user_name == 'admin' already exists, it does nothing.

    """
    configfile = find_config(args)
    turbogears.update_config(configfile=configfile,
        modulename="eggbasket.config")
    from turbogears import database
    model = get_model()
    session = database.session
    database.bind_meta_data()
    database.metadata.create_all(database.get_engine())

    try:
        session.query(model.User).filter_by(user_name=u'admin').one()
    except model.InvalidRequestError:
        adminuser = model.User(display_name=u"Administrator", user_name=u"admin",
            password=u"admin", email_address=u"admin@localhost.localdomain")
        maintgroup = model.Group(display_name=u"Package maintainers",
            group_name=u"maintainer")
        admingroup = model.Group(display_name=u"Administrators",
            group_name=u"admin")
        adminuser.groups.append(maintgroup)
        adminuser.groups.append(admingroup)
        uploadperm = model.Permission(permission_name=u"upload",
            description=u"Can upload package files")
        dloadperm = model.Permission(permission_name=u"download",
            description=u"Can download package files")
        uploadperm.groups.append(maintgroup)
        session.flush()
    else:
        print "There already is an 'admin' user in the database."

def start_server(args):
    """Start the CherryPy application server."""
    configfile = find_config(args)
    turbogears.update_config(configfile=configfile,
        modulename="eggbasket.config")
    from eggbasket.controllers import Root
    turbogears.start_server(Root())

def main():
    from eggbasket import __version__
    parser = optparse.OptionParser(prog='eggbasket-server',
        version=__version__)
    parser.add_option("-i", "--init", action="store_true",
        help="Init database only, don't start server.",
        dest="init", default=False)
    (options, args) = parser.parse_args()

    if options.init:
        init_database(args)
    else:
        start_server(args)

if __name__ == '__main__':
    main()
