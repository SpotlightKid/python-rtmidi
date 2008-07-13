# -*- coding: UTF-8 -*-

import cherrypy

from turbogears import controllers, expose, flash, redirect, url

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
            # FIXME: should redirect to where controller is mounted
            redirect('/')
        else:
            return action(item, *vpath[2:], **params)

    def query(self, id):
        """Should be overwritten in subclass."""

        return None

#################
# Example usage #
#################

from myproject.model import Item
from myproject.widgets import editform

class ItemsController(RESTController):
    
    @expose(template='.templates.items.list')
    def index(self):
        title = _(u'List of items')
        heading = _(u'Your items')
        bookmarks = Item.select()
        return dict(items=items, title=title, heading=heading)

    @expose(template='.templates.items.edit')
    def view(self, item=None, *args, **kw):
        if bookmark is None:
            form_data = {}
            placeholders = dict(
                title = _(u'Add new item'),
                heading = _(u'Enter data for new item'),
            )
            form_params = dict(
                submit_text = _(u'Add item'),
                action = 'create',
            )
        else:
            form_data = dict(
                title = item.title,
                description = item.description,
                # ...
            )
            placeholders = dict(
                title = _(u'Update item'),
                heading = _(u'Change item data'),
            )
            form_params = dict(
                submit_text = _(u'Update item'),
                action = 'update',
            )
        return dict(
            form=editform,
            from_data=form_data,
            form_params=form_params,
            **placeholders
        )
    
    edit = view
    add = view

    @expose()
    @validate(form=editform)
    @error_handler(view)
    def update(self, item=None, *args, **data):
        """Handle POST requests with item data."""
        
        # data should be cleaned up and validated by now
        if item:
            item.set(**data)
        else:
            item = Item(**data)
        # do other things with item here

    create = update

    def query(self, id):
        return Item.get(id)
