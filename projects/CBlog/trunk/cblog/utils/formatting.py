# -*- coding: UTF-8 -*-

from urllib import quote as urlquote

import cElementTree as ET

from turbogears import config, url
from dateutil import tz

__all__ = [
    'esc',
    'esq',
    'escs',
    'esqs',
    'format_author',
    'format_date',
    'format_filesize',
    'format_tags',
    'plural',
]

def _escape(s, quote=False):
    # These substitutions are copied from cgi.escape().
    s = s.replace("&", "&amp;") # Must be done first!
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    if quote:
        s = s.replace('"', "&quot;")
    return s
esc = _escape
esq = lambda x: _escape(x, True)
escs = lambda x: _escape(str(x))
esqs = lambda x: _escape(str(x), True)

def format_author(comment):
    if comment.homepage:
        el = ET.Element('a', href=comment.homepage)
        el.text = comment.author
        return el
    else:
        return comment.author

def format_date(date):
    # assume date is UTC if tzinfo is not set
    # and convert it to a timezone aware date(time) object
    if not date.tzinfo:
        timezone = config.get('cblog.timezone')
        if not timezone:
            tzinfo = tz.gettz()
        else:
            tzinfo = tz.tzstr(timezone)
        date = date.replace(tzinfo=tzinfo)
    fmt = config.get('cblog.date_format', '%X')
    return date.strftime(fmt)

def format_tags(tags, sep=', '):
    out = []
    for tag in tags:
        u = url('/tag/%s' % tag.name.encode('utf-8'))
        out.append('<a class="tag" href="%s">%s</a>' %
          (urlquote(u), esc(tag.name)))
    return sep.join(out)

def format_filesize(size):
    """Format file size in bytes in human-readable format."""

    kb = size / 1024.
    if kb < 1024:
        return u"%.2f Kb" % kb
    mb = kb / 1024.
    if mb < 1024:
        return u"%.2f Mb" % mb
    return u"%.2f Gb" % (mb / 1024.,)

def plural(num, singular, plural):
    return num!=1 and plural or singular
