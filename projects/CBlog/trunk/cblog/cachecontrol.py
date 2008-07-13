import logging
from time import strftime, gmtime, time

import cherrypy
from turbogears import config

log = logging.getLogger('cblog.controllers')

time_fmt = '%a, %d %b %Y %H:%M:%S GMT'

class ExpiresFilter(cherrypy.filters.basefilter.BaseFilter):


    def before_finalize(self):
        rh = cherrypy.response.headerMap
        if config.get('expiresFilter.on', False) and \
          'no-cache' not in rh.get('Pragma', ''):
            log.debug('Adding cache control headers.')

            now = time()
            cache_seconds = config.get('expiresFilter.seconds ', 300)

            rh['Last-Modified'] = strftime(time_fmt, gmtime(now))
            rh['Expires'] = strftime(time_fmt, gmtime(now + cache_seconds))
        else:
            log.debug('Caching disabled!')

        rh['Vary'] = 'Cookie'

def strongly_expire(func):
    """Decorator to add response headers that instruct browsers and proxies not to cache.
    """

    def newfunc(*args, **kwargs):
        rh = cherrypy.response.headerMap
        rh['Expires'] = strftime(time_fmt, 0)
        rh['Cache-Control'] = \
          'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
        rh['Pragma'] = 'no-cache'
        return func(*args, **kwargs)

    return newfunc
