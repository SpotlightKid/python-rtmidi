from Cheetah.Filters import Filter
from Cheetah.Template import Template

from turbogears import url

from cElementTree import iselement

from cblog.widgets.base import serialize_et
from cblog.utils.formatting import *

class HSC(Filter):
    """A filter for Cheetah placeholder substitution supporting unicode objects.

    Supports the following arguments:

    encoding  - encode unicode string with the given encoding (default: utf-8).
    escape    - if evaluates to True, escape HTML special chars when
                substituting the placeholder. If escape == 'quote', also
                replace '"' with '&quot;'.
    maxlength - if set to an int > 0, truncate the placeholder substitution at
                max maxlength characters, possibly replacing the end with
                suffix.
    suffix    - when truncating the placeholder to maxlength, replace the last
                len(suffix) characters with suffix (default '...').
    """

    def filter(self, val, **kw):
        if val is None:
            return ''
        if iselement(val):
            val = serialize_et(val)
        if isinstance(val, unicode):
            val = val.encode(kw.get('encoding', 'utf-8'))
        val = str(val)
        if kw.get('escape', False):
            val = esc(val, kw.get('escape') == 'quote')
        if kw.get('maxlength'):
            try:
                length = int(kw['maxlength'])
            except ValueError: pass
            else:
                suffix = kw.get('suffix', '...')
                if len(val) > length and suffix:
                    length -= len(suffix)
                    val = val[:length] + suffix
                else:
                    val = val[:length]
        return val

class SiteBase(Template):

    img_base = url('/static/images/')
    css_base = url('/static/css/')
    js_base = url('/static/javascript/')

    _js_src_tmpl = '<script%s>\n%s\n</script>'
    _js_link_tmpl = '<script src="%s"%s></script>'
    _css_link_tmpl = '<link href="%s"%s />'

    def __init__(self, *args, **kw):
        """Constructor sets the default filter to use."""

        kw['filter'] = HSC
        super(SiteBase, self).__init__(*args, **kw)

    def js_src(self, code, **attrs):
        attrs.setdefault('type', 'text/javascript')
        attrs = self._make_attrs(attrs)
        return self._js_src_tmpl % (attrs, code)

    def js_link(self, relpath, **attrs):
        attrs.setdefault('type', 'text/javascript')
        attrs = self._make_attrs(attrs)
        return self._js_link_tmpl % (self.js_base + relpath, attrs)

    def css_link(self, relpath, **attrs):
        attrs.setdefault('type', 'text/css')
        attrs.setdefault('rel', 'stylesheet')
        attrs = self._make_attrs(attrs)
        return self._css_link_tmpl % (self.css_base + relpath, attrs)

    def _make_attrs(self, attrs):
        return ''.join([' %s="%s"' % (esc(k), esqs(v))
          for k,v in attrs.items()])

    # more utility functions
    def yesno(self, flag):
        if flag:
            return _(u'yes')
        else:
            return _(u'no')
