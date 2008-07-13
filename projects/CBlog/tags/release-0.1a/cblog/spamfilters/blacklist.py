blacklist = [
    '127.0.0.1'
]
import logging

log = logging.getLogger("turbogears.controllers")

def filter(value, state=None):
    request = state.get('request')
    log.info('Comment submission from IP %s' % getattr(request, 'remote_addr', 
      '<unknown>'))
    if request and request.remote_addr in blacklist:
        return 10
    return 0
