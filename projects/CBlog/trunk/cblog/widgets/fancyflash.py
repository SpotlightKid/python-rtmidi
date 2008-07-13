__all__ = ['FancyFlash']

import pkg_resources

from turbogears.widgets import Widget, JSSource, JSLink, CSSLink, \
  js_location, register_static_directory

from simplejson import loads

from cblog.widgets import jslibs

static_dir = pkg_resources.resource_filename("cblog", "static")
register_static_directory("fancyflash", static_dir)

fancyflash_css = [CSSLink("fancyflash", "css/fancyflash.css", media="screen")]
fancyflash_js = [
  jslibs.events,
  JSLink("fancyflash", "javascript/fancyflash.js"),
  JSSource(
    "document.write('<style>#statusmessage {position: absolute;}</style>');",
    js_location.head
  )
]

def _escape(s, quote=False):
    # These substitutions are copied from cgi.escape().
    s = s.replace("&", "&amp;") # Must be done first!
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    if quote:
        s = s.replace('"', "&quot;")
    return s

class FancyFlash(Widget):
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

    def update_params(self, params):
        super(FancyFlash, self).update_params(params)
        params.update(self._parse_tg_flash(params.get('value')))

    def _parse_tg_flash(self, tg_flash):
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
