import cherrypy

import turbogears
from turbogears import controllers, expose, redirect, validate, url

from flashcontroller import FlashTestController

class Root(controllers.RootController):
    flash = FlashTestController()

    @expose()
    def index(self):
        redirect(url('/flash'))
