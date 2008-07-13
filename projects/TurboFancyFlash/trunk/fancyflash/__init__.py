# -*- coding: UTF-8 -*-
"""Functions for displaying status messages on the next page.

Intended as drop-in replacement and building on turbogears.flash() but
allow for much nicer styling of the messages, since you can pass a "status"
parameter, which will be used for the CSS class of the DIV element that
encloses the status message.
"""
__docformat__ = 'restructuredtext'

__all__ = [
    'error',
    'fancyflashwidget',
    'info',
    'register_flash_widget',
    'set_default_flash_timeout',
    'statusmessage',
    'success',
    'warning'
]

import turbogears
from simplejson import dumps

from widgets import FancyFlashWidget

fancyflashwidget = FancyFlashWidget()

_default_timeout = 0
def set_default_flash_timeout(timeout):
    """Set the default timeout after which the message box disappears."""

    global _default_timeout
    _default_timeout = timeout

def register_flash_widget(widget='fancyflash.fancyflashwidget'):
    """Register FancyFlashWidget to be included on every page."""

    # first get widgets listed in the config files
    include_widgets = turbogears.config.get('tg.include_widgets', [])
    # then append FancyFlash widget
    include_widgets.append(widget)
    turbogears.config.update(
        {'global': {'tg.include_widgets': include_widgets}}
    )
    return widget

def statusmessage(msg, status="info", timeout=0, allow_html=False):
    """Display fancy flash window with message ``msg`` on the next page.
    
    ``status`` - string, which will be used as the css class for the
    inner DIV element of the message window. The default CSS supports 
    different styles and icons for status "info", "success", "warning"
    and "error".
    
    ``timeout`` - number of seconds after which the message will fade out.
    The client needs to have JavaScript enabled for this to work. Default
    is ``0``, i.e. the message stays until the user clicks on it.
    
    ``allow_html``- normally, HTML markup in ``msg`` is escaped for security
    reasons. Set this to ``True`` to allow usage of HTML markup in the message
    text.

    """
    assert isinstance(status, basestring)
    tg_flash = dict(msg=msg, status=status)
    if timeout:
        tg_flash['timeout'] = timeout
    elif _default_timeout:
        tg_flash['timeout'] = _default_timeout
    if allow_html:
        tg_flash['allow_html'] = True
    turbogears.flash(dumps(tg_flash))

def error(msg, timeout=0, allow_html=False):
    """Display fancy flash window with message ``msg`` and status "error".
    
    For the ``timeout`` and ``alllow_html`` arguments, see the documentation
    for the ``statusmessage`` funcion.
    
    """
    statusmessage(msg, "error", timeout, allow_html=allow_html)

def info(msg, timeout=0, allow_html=False):
    """Display fancy flash window with message ``msg`` and status "info".
    
    For the ``timeout`` and ``alllow_html`` arguments, see the documentation
    for the ``statusmessage`` funcion.
    
    """
    statusmessage(msg, "info", timeout, allow_html=allow_html)

def success(msg, timeout=0, allow_html=False):
    """Display fancy flash window with message ``msg`` and status "success".
    
    For the ``timeout`` and ``alllow_html`` arguments, see the documentation
    for the ``statusmessage`` funcion.
    
    """
    statusmessage(msg, "success", timeout, allow_html=allow_html)

def warning(msg, timeout=0, allow_html=False):
    """Display fancy flash window with message ``msg`` and status "warning".
    
    For the ``timeout`` and ``alllow_html`` arguments, see the documentation
    for the ``statusmessage`` funcion.
    
    """
    statusmessage(msg, "warning", timeout, allow_html=allow_html)
