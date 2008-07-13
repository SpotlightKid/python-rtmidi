# -*- coding: UTF-8 -*-

import logging
import os

import cherrypy as cp
import turbogears as tg

try:
    from dbsprockets.dbmechanic.frameworks.tg import DBMechanic
    from dbsprockets.saprovider import SAProvider
    has_dbsprockets = True
except ImportError:
    has_dbsprockets = False

from eggbasket import model

log = logging.getLogger("eggbasket.controllers")


class AdminController(tg.controllers.Controller, tg.identity.SecureResource):
    """Controller for administration and configuration pages."""

    require = tg.identity.in_group('admin')

    @tg.expose(template="eggbasket.templates.admin")
    def index(self, *args, **kw):
        """Show administration start page."""
        pkg_root = tg.config.get('eggbasket.package_root', os.getcwd())
        return dict(pkg_root=pkg_root, has_dbsprockets=has_dbsprockets)

    # Very basic database administration iterface provided by DBMechanic
    if has_dbsprockets:
        database = DBMechanic(SAProvider(model.metadata), '/admin/database')
