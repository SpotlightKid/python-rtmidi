# -*- coding: UTF-8 -*-

__all__ = ['CBlogFeedController']

import logging

from os.path import splitext
from urllib import urlencode

from turbogears import config, expose, url
from turbogears.feed import FeedController

from sqlobject import SQLObjectNotFound
from sqlobject.sqlbuilder import *
from cblog import model
from cblog.utils.misc import absolute_url

log = logging.getLogger('cblog.controllers')

class CBlogFeedController(FeedController):
    """Blog controller for RSS/Atom feed generation."""

    def __init__(self, path):
        super(CBlogFeedController, self).__init__()
        # FIXME: can you determine the mount-point if the controller otherwise?
        self.path = path

    title = config.get('cblog.title')
    author = config.get('cblog.author')
    subtitle = config.get('cblog.description')

    expose(template='cblog.templates.feed.atom1_0', format='xml',
      content_type='application/atom+xml')
    def atom1_0(self, *args, **kw):
        if args and args[0] in ['full', 'summary']:
            kw['format'] = args[0]
        feed = self.get_feed_data(**kw)
        self.format_dates(feed, 3339)
        try:
            url_params = dict(tag=feed['categories'][0])
        except (KeyError, IndexError):
            url_params = {}
        feed.update(self.get_feed_info('atom1_0',
          format=kw.get('format', 'summary'), **url_params))
        feed['id'] = feed['href']
        return feed

    def get_feed_data(self, **kw):
        """Fetch feed data from model and assemble into dictionary."""

        feed = dict(
            title = self.title,
            author = dict(name=self.author),
            subtitle = self.subtitle,
            categories = []
        )
        if config.get('cblog.feed.logo'):
            feed['logo'] = url('/static/images/' + config.get('cblog.feed.logo'))

        tag = kw.get('tag')
        if tag:
            try:
                tag = model.Tag.select(
                  func.LOWER(model.Tag.q.name) == tag.lower())[0]
            except (SQLObjectNotFound, IndexError):
                raise cherrypy.HTTPError(status=404)
            else:
                entries = list(tag.entries)
                feed['categories'].append(tag.name)
                feed['title'] += ' (%s %s)' % (_(u'Category'), tag.name)
        else:
            entries = list(model.Entry.select(orderBy='-created'))

        if entries:
            # feed update timestamp == creation time of last entry
            feed['updated'] = entries[0].created

        feed_entries = []
        for entry in entries:

            feed_entry = dict(
              link = absolute_url('article/%s' % entry.id),
              published = entry.created,
              title = entry.title,
              author = dict(name=entry.author.display_name),
              summary = entry.teaser,
              categories = [tag.name for tag in entry.tags]
            )
            if kw.get('format') == 'full':
                feed_entry['content'] = dict(type='html', value=entry.html_text)
            if entry.comment_count:
                feed_entry['updated'] = entry.comments[0].created
            else:
                feed_entry['updated'] = entry.created
            feed_entries.append(feed_entry)
        feed['entries'] = feed_entries

        return feed

    def get_feed_info(self, version='atom1_0', **kw):
        """Return dictionary with basic info about this feed.

        Returned dict has two keys:

           # href -- the absolute URL of the feed
           # title -- the title of the feed
        """

        info = dict(
            title=config.get('cblog.title'),
            href=self.get_feed_url(version, **kw)
        )
        tag = kw.get('tag')
        if tag:
            info['title'] += ' (%s %s)' % (_(u'Category'), tag)
        return info

    def get_feed_url(self, version='atom1_0', name=None, format='full', **kw):
        """Return absolute URL for the feed."""

        if name is None:
            name = version + '.xml'

        base_url = absolute_url('%s/%s/%s/%s' % \
          (self.path, version, format, name), **kw
        )
        return base_url
