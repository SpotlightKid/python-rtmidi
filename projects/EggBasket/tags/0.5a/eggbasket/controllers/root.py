"""The EggBasket root controller."""
# -*- coding: UTF-8 -*-

import logging
import os

from os.path import join

import cherrypy as cp
import turbogears as tg

from eggbasket import __version__
from eggbasket import model
from eggbasket.controllers.errorcatcher import ErrorCatcher
from eggbasket.controllers.admin import AdminController
from eggbasket.controllers.packages import PackageController
from eggbasket.util import is_package_dir
# from eggbasket import json
from eggbasket.util import txt2html


log = logging.getLogger("eggbasket.controllers")

def add_sitevars(vars):
    """Add site information to standard template variables."""
    vars['sitename'] = tg.config.get('eggbasket.sitename',
        'EggBasket Package Index')
    vars['server_version'] = __version__

tg.view.variable_providers.append(add_sitevars)

def get_static_content(name):
    """Read text file from static directory and covert to HTML."""
    static_dir = tg.config.get('static_filter.dir', path='/static')
    filename = join(static_dir, name)
    try:
        fo = open(filename, 'rb')
    except (OSError, IOError):
        text = _(u"Could not read static content resource '%s'.") % name
    else:
        text = fo.read().decode('utf-8')
        fo.close()
    return txt2html(text)


class Root(ErrorCatcher):
    """The root controller of the EggBasket application."""

    admin = AdminController()
    package = PackageController()

    @tg.expose()
    def index(self, *args, **kw):
        """Delegate requests for front page to package list.

        Might be replaced by a welcome / search page sometime.

        """
        #tg.redirect('/package')
        return self.package.index(*args, **kw)
    simple = index

    @tg.expose()
    def default(self, package=None, *args, **kw):
        """Delegate requests with package name to PackageController."""
        #tg.redirect('/package/%s' % package)
        return self.package.default(package, *args, **kw)

    @tg.expose()
    def upload(self, *args, **kw):
        """Delegate package uploads to PackageController."""
        return self.package.upload(*args, **kw)

    @tg.expose(template="eggbasket.templates.generic")
    def about(self, package=None):
        """Display information page about the software."""
        content = get_static_content('about.rst')
        return dict(
            title=_(u'About'),
            heading=_(u'About the EggBasket Software'),
            content=content
        )

    @tg.expose(template="eggbasket.templates.generic")
    def help(self, package=None):
        """Display usage information for the software."""
        content = get_static_content('help.rst')
        return dict(
            title=_(u'Help'),
            heading=_(u'How to use EggBasket'),
            content=content
        )

    @tg.expose(template="eggbasket.templates.login")
    def login(self, forward_url=None, previous_url=None, *args, **kw):
        """Display the login form."""
        if not tg.identity.current.anonymous \
                and tg.identity.was_login_attempted() \
                and not tg.identity.get_identity_errors():
            tg.redirect(tg.url(forward_url or previous_url or '/', kw))

        forward_url = None
        previous_url = cp.request.path

        if tg.identity.was_login_attempted():
            msg = _("The credentials you supplied were not correct or "
                   "did not grant access to this resource.")
        elif tg.identity.get_identity_errors():
            msg = _("You must provide your credentials before accessing "
                   "this resource.")
        else:
            msg = _("Please log in.")
            forward_url = cp.request.headers.get("Referer", "/")

        cp.response.status = 401
        return dict(message=msg, previous_url=previous_url, logging_in=True,
            original_parameters=cp.request.params, forward_url=forward_url)

    @tg.expose()
    def logout(self):
        """Clear current identity and redirect to front page."""
        tg.identity.current.logout()
        tg.redirect("/")
