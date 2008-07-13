# -*- coding: UTF-8 -*-

import logging
import time

import cherrypy

import turbogears
from turbogears import controllers, expose, identity, redirect

from tgfastdata import DataController

from bookmarker.model import User
from bookmarker.subcontrollers import *

log = logging.getLogger("bookmarker.controllers")

class Root(controllers.RootController):

    bookmarks = BookmarksController()

    users = DataController(User, object_name='User',
        list_fields=['id', 'user_name', 'display_name', 'password'],
        list_template='bookmarker.templates.users.list',
        form_template='bookmarker.templates.users.edit')
    users = identity.SecureObject(users, identity.has_permission('admin'))

    @expose(template="bookmarker.templates.welcome")
    def index(self):
        return dict(now=time.ctime())

    @expose(template="bookmarker.templates.login")
    def login(self, forward_url=None, previous_url=None, *args, **kw):

        if not identity.current.anonymous \
            and identity.was_login_attempted() \
            and not identity.get_identity_errors():
            raise redirect(forward_url)

        forward_url=None
        previous_url= cherrypy.request.path

        if identity.was_login_attempted():
            msg=_("The credentials you supplied were not correct or "
                   "did not grant access to this resource.")
        elif identity.get_identity_errors():
            msg=_("You must provide your credentials before accessing "
                   "this resource.")
        else:
            msg=_("Please log in.")
            forward_url= cherrypy.request.headers.get("Referer", "/")
        cherrypy.response.status=403
        return dict(message=msg, previous_url=previous_url, logging_in=True,
                    original_parameters=cherrypy.request.params,
                    forward_url=forward_url)

    @expose()
    def logout(self):
        identity.current.logout()
        raise redirect("/")
