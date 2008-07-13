# -*- coding: UTF-8 -*-

import logging
from cgi import escape

from turbogears import controllers, expose, validate, redirect
from turbogears import identity, config, url, flash, error_handler

from sqlobject import *

from bookmarker.model import *
from bookmarker.subcontrollers.base import RESTController
from bookmarker.widgets import *

log = logging.getLogger("bookmarker.controllers")

class BookmarksController(RESTController, identity.SecureResource):
    require = identity.not_anonymous()

    @expose(template='bookmarker.templates.bookmarks.list')
    def index(self):
        title = _(u'%s\'s bookmarks' % identity.current.user.display_name)
        heading = _(u'Your bookmarks')
        bookmarks = Bookmark.select(
            Bookmark.q.ownerID == identity.current.user.id
        )
        return dict(entries=bookmarks, title=title, heading=heading)

    @expose(template='bookmarker.templates.bookmarks.list')
    def tag(self, name):
        title = _(u'%s\'s bookmarks' % identity.current.user.display_name)
        heading = _(u'Your bookmarks with tag "%s"') % name
        tags = list(Tag.select(AND(
            Tag.q.name == name, 
            Tag.q.ownerID == identity.current.user.id)
        ))
        if tags:
            bookmarks = tags[0].bookmarks
        else:
            bookmarks = []
        return dict(entries=bookmarks, title=title, heading=heading)

    @expose(template='bookmarker.templates.bookmarks.edit')
    def view(self, bookmark=None, *args, **kw):
        if bookmark is None:
            data = {}
            placeholders = dict(
                title = _(u'Bookmarker: Add new bookmark'),
                heading = _(u'Enter data for new bookmark'),
                submit_text = _(u'Add bookmark'),
                action = 'create',
            )
        else:
            data = dict(
                id = bookmark.id,
                title = bookmark.title,
                url = bookmark.url,
                description = bookmark.description,
                tags = ', '.join([tag.label for tag in bookmark.tags])
            )
            placeholders = dict(
                title = _(u'Bookmarker: Edit bookmark'),
                heading = _(u'Change bookmark data'),
                submit_text = _(u'Update bookmark'),
                action = 'update',
            )
        return dict(data=data, form=bookmarkform, **placeholders)
    edit = view

    @expose(template='bookmarker.templates.bookmarks.edit')
    def add(self):
        """The add method is only an alias for the 'view' method too.
        
        The view method handles the case were no bookmark is specified
        and just displays an empty form.
        """
        
        return self.view()

    @expose()
    @validate(form=bookmarkform)
    @error_handler(view)
    def update(self, bookmark=None, *args, **kw):
        """Handle POST requests with bookmark data."""

        data = dict(
            title = kw['title'],
            url = kw['url'],
            description = kw.get('description')
        )
        if bookmark:
            bookmark.set(**data)
        else:
            bookmark = Bookmark(owner=identity.current.user, **data)

        tags = kw.get('tags')
        if tags:
            tags = [tag.strip() for tag in tags.split(',')]
            bookmark.update_tags(tags)
        flash('Bookmark saved!')
        redirect('/bookmarks/%i/view' % bookmark.id)
    create = update

    def query(self, id):
        return Bookmark.get(id)
