"""Functions for displaying status messages on the next page.

Intended as drop-in replacement and building on turbogears.flash() but
allow for much nicer styling of the messages, since you can pass a "status"
parameter, which will be used for the CSS class of the DIV element that
encloses the status message.
"""

__all__ = [
    'error',
    'info',
    'set_default_message_timeout',
    'statusmessage',
    'success',
    'warning'
]

import turbogears
from simplejson import dumps

_default_timeout = 0
def set_default_message_timeout(timeout):
    """Set the default timeout after which the message box disappears."""

    global _default_timeout
    _default_timeout = timeout


def statusmessage(msg, status="info", timeout=0, allow_html=False):
    assert isinstance(status, basestring)
    tg_flash = dict(msg=msg, status=status)
    if timeout:
        tg_flash['timeout'] = timeout
    elif _default_timeout:
        tg_flash['timeout'] = _default_timeout
    if allow_html:
        tg_flash['allow_html'] = True
    turbogears.flash(dumps(tg_flash))

def info(msg, timeout=0, allow_html=False):
    statusmessage(msg, "info", timeout)

def error(msg, timeout=0, allow_html=False):
    statusmessage(msg, "error", timeout)

def warning(msg, timeout=0, allow_html=False):
    statusmessage(msg, "warning", timeout)

def success(msg, timeout=0, allow_html=False):
    statusmessage(msg, "success", timeout)
