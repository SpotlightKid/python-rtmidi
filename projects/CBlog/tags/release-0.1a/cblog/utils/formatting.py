# -*- coding: UTF-8 -*-

from urllib import quote as urlquote
from turbogears import config, url

import cElementTree as ET

__all__ = [
    'escape',
    'format_date',
    'format_tags',
    'format_author'
]

def escape(s, quote=False):
    # These substitutions are copied from cgi.escape().
    s = s.replace("&", "&amp;") # Must be done first!
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    if quote:
        s = s.replace('"', "&quot;")
    return s

def format_date(date):
    fmt = config.get('cblog.date_format', '%X')
    return date.strftime(fmt)

def format_tags(tags, sep=', '):
    out = []
    for tag in tags:
        u = url('/tag/%s' % tag.name.encode('utf-8'))
        out.append('<a class="tag" href="%s">%s</a>' %
          (urlquote(u), escape(tag.name)))
    return sep.join(out)

def format_author(comment):
    if comment.homepage:
        el = ET.Element('a', href=comment.homepage)
        el.text = comment.author
        return el
    else:
        return comment.author
