"""TurboGears widget for gravatars (globally recognized user icons).

See <http://gravatar.com/implement.php> for more info.

Usage
-----

Controller::

    from gravatar import Gravatar

    class Root:
        @expose()
        def index(self):
            return {'gravatar': Gravatar(size=50)}

Template::

    ${gravatar.display('joe@foo.com')}
"""

__all__ = [
  'Gravatar',
  'GravatarController'
]

import md5
import os
from os.path import exists, join
from urllib import quote_plus, unquote
import pkg_resources
import cherrypy
from turbogears import config, controllers, expose, redirect, url
from turbogears.widgets import *

from cblog.widgets import jslibs

js_dir = pkg_resources.resource_filename("cblog.widgets.gravatar",
  "static/javascript")
register_static_directory("gravatar", js_dir)

GRAVATAR_WIDGET_JS = """
/* Hide gravatar icons initially only when Javascript is enabled */
document.write('<style>.gravatar {display: none;}</style>');
"""

class Gravatar(Widget):
    """A gravatar icon representing a user in a blog comment/forum post/etc."""

    name = 'gravatar'

    template = """\
    <img xmlns:py="http://purl.org/kid/ns#" py:if="hash"
      width="${size}" height="${size}" py:attrs="attrs"
      src="${url}?gravatar_id=${hash}&amp;size=${size}${rating}${default}" />
    """

    params = ['attrs', 'default', 'rating', 'size', 'url']

    # Parameter default values
    attrs = {}
    rating = 'R'
    default = None
    url = 'http://www.gravatar.com/avatar.php'
    size = 80

    # Attached JavaScript
    javascript = [
      jslibs.events,
      JSLink("gravatar", "gravatar.js"),
      JSSource(GRAVATAR_WIDGET_JS, js_location.head)
    ]

    params_doc = dict(
      attrs='Dictionary containing extra (X)HTML attributes for the IMG tag',
      default='URL of default image to return if gravatar is not available.',
      rating='Highest acceptable rating of returned gravatar (G|PG|R|X)',
      size='Size of returned gravatar image in pixels.',
      url='URL of gravatar server. Default: %s' % url
    )

    def update_params(self, params):
        """Builds hash from email given on widget display & creates gravatar URL.
        """

        super(Gravatar, self).update_params(params)
        email = params.get('value')
        if email:
            params['hash'] = md5.new(email).hexdigest()
        else:
            params['hash'] = None
        default = params.get('default')
        if default:
            params['default'] = '&default=%s' % quote_plus(default)
        rating = params.get('rating')
        if rating in ['G', 'PG', 'R', 'X']:
            params['rating'] = '&rating=%s' % rating
        else:
            params['rating']
        params['url'] = url(params['url'])
        params['attrs'].setdefault('class', 'gravatar')

import logging
log = logging.getLogger('cblog.controllers')

class GravatarController(controllers.Controller):

    def __init__(self, cache_dir=None, mirror=Gravatar.url):
        self.cache_dir = cache_dir
        if not cache_dir:
            self.cache_dir = join(
              config.get('static_filter.dir', path="/static"),
              'images', 'gravatars')

        self.mirror = mirror
        if self.cache_dir:
            cherrypy.config.update({
              '/gravatars': {
                'static_filter.on': True,
                'static_filter.dir': self.cache_dir
              }
            })
        self.on_cache_miss = config.get('gravatars.on_cache_miss', 'redirect')

    expose()
    def default(self, gravatar_id=None, size=80, rating='R', default=None):
        if not gravatar_id:
            raise cherrypy.NotFound
        suffix = '?gravatar_id=%s&size=%s&rating=%s' % \
          (gravatar_id, size, rating)
        gid = md5.new(suffix).hexdigest()
        if not self.cache_dir or \
          not os.access(join(self.cache_dir, gid + '.png'), os.R_OK):
            log.info('Gravatar request: %s' % suffix)
            if default:
                if self.on_cache_miss == 'default':
                    redirect(default)
                suffix += '&default=%s' % default
            redirect(self.mirror + suffix)
        else:
            redirect('/gravatars/%s.png' % gid)
