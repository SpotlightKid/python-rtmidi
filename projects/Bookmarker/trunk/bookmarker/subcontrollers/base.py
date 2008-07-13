# -*- coding: UTF-8 -*-

import cherrypy

from turbogears import controllers, expose, flash, redirect, url

from sqlobject import SQLObjectNotFound

class RESTController(controllers.Controller):

    @expose()
    def default(self, *vpath, **params):
        """REST dispatcher. Allows URLs like http://mysite/objects/n/verb.

        See: http://trac.turbogears.org/turbogears/wiki/RestfullPath
        """

        if len(vpath) == 1:
            id = vpath[0]
            if cherrypy.request.method.lower() == 'post':
                # FIXME: May break @validate
                action = self.update
            else:
                redirect(url('%s/view') % id)
        elif len(vpath) >= 2:
            id, verb = vpath[:2]
            verb = verb.replace('.', '_')
            action = getattr(self, verb, None)
            # FIXME: check if action allows request method
            # and raise cherrypy.HTTPError(405) if not (decorator?)
            if not action or not getattr(action, 'exposed'):
                raise cherrypy.NotFound
        else:
            raise cherrypy.NotFound
        try:
            item = self.query(int(id))
        except:
            flash("Object '%s' not found." % id)
            redirect('/bookmarks/')
        else:
            return action(item, *vpath[2:], **params)

    def query(self, id):
        """Should be overwritten in subclass."""
        return None
