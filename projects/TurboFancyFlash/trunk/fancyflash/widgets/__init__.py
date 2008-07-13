# -*- coding: UTF-8 -*-
"""TurboGears widgets for displaying fancy flash message boxes."""
__docformat__ = 'restructuredtext'

__all__ = ['FancyFlashWidget', 'FancyFlashDesc']

import pkg_resources

from turbogears.widgets import Widget, WidgetDescription, JSSource, JSLink, \
    CSSLink, js_location, register_static_directory

from simplejson import loads

import jslibs

static_dir = pkg_resources.resource_filename("fancyflash.widgets", "static")
register_static_directory("fancyflash", static_dir)

fancyflash_css = [CSSLink("fancyflash", "css/fancyflash.css", media="screen")]
fancyflash_js = [
  jslibs.mochikit,
  jslibs.events,
  JSLink("fancyflash", "javascript/fancyflash.js"),
  JSSource("write_stylesheet();", js_location.head)
]

def _escape(s, quote=False):
    # These substitutions are copied from cgi.escape().
    s = s.replace("&", "&amp;") # Must be done first!
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    if quote:
        s = s.replace('"', "&quot;")
    return s

class FancyFlashWidget(Widget):
    """A message box with a status icon and background color based on status.
    
    With JavaScript support enabled, can be positioned absolutely and on top
    of the normal page content. The user can then click the message to make it
    go away, or the message disappears after a cretain timeout. If JavaScript
    is disabled. The message box will be display diretcly where the widget is
    inserted in the template.
    """

    name = "statusmessage"
    template = """
<div xmlns:py="http://purl.org/kid/ns#" id="statusmessage">
  <!--[if gte ie 5.5000]>
  <link rel="stylesheet" type="text/css"
    href="/tg_widgets/fancyflash/css/ie.css">
  <![endif]-->
  <div py:if="message" class="${status}" py:content="XML(message)"></div>
  <script py:if="timeout" py:replace="script()" />
</div>
"""
    params = ['message', 'status', 'timeout']
    message = ''
    status = 'info'
    timeout = 0
    css = fancyflash_css
    javascript = fancyflash_js

    params_doc = {
        'message': 'The message test to display.',
        'status': 'The status name, which will be used as the CSS class '
            'of the inner DIV element.',
        'timeout': 'The number of seconds after which the message will fade '
            'out. Needs JavaScript enabled to work. Default is 0, i,e, the '
            'message will stay until the user clicks on it.',
    }

    def update_params(self, params):
        """Decode tg_flash string passed as value and set params from result.
        """
        super(FancyFlashWidget, self).update_params(params)
        params.update(self._parse_tg_flash(params.get('value')))

    def _parse_tg_flash(self, tg_flash):
        """Try to decode given string as JSON and extract widget params."""
        params = dict()
        if tg_flash:
            try:
                tg_flash = loads(tg_flash)
            except:
                tg_flash = dict(msg=tg_flash)
            else:
                if not (isinstance(tg_flash, dict) and tg_flash.has_key('msg')):
                    if isinstance(tg_flash, basestring):
                        tg_flash = dict(msg=tg_flash)
                    else:
                        tg_flash = dict(msg=str(tg_flash))
            msg = tg_flash.get('msg')
            if msg:
                if not tg_flash.get('allow_html', False):
                    msg = _escape(msg)
                params['message'] = msg
                params['status'] = tg_flash.get('status', 'info')
                try:
                    params['timeout'] = int(tg_flash.get('timeout', 0))
                except ValueError: pass
                else:
                    if params['timeout'] > 0:
                        params['script'] = JSSource("setHideTimeout('%s', %s);" \
                          % (self.name, params['timeout']))
        return params

class FancyFlashDesc(WidgetDescription):
    name = "Fancy Flash Message"
    for_widget = FancyFlashWidget()
    template = """\
    <div>
        ${for_widget("This is a Fancy Flash Message!", status="info",
            timeout="10")}
    </div>
    """
