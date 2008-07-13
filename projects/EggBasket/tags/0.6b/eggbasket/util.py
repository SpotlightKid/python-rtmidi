# -*- coding: UTF-8 -*-

__all__ = [
    'has_extension',
    'is_package_dir',
    'is_package_file',
    'munge_pkg_info',
    'txt2html',
]

import os
import re
import string

import cherrypy as cp
import turbogears as tg

from eggbasket.odict import OrderedDict

try:
    from eggbasket.rest import HTML
    tg.config.update({'has_docutils': True})
except ImportError:
    tg.config.update({'has_docutils': False,
        'eggbasket.pkg_desc_format': 'plain'})


_email_rx = re.compile(r'([-\w.+]+@[\w.]+?\.\w+)')
def _make_link(s):
    """Turn HTTP URLs and emails adresses into HTML link elements."""
    if _email_rx.search(s):
        return dict(value=s,
            html=_email_rx.sub(r'<a href="mailto:\1">\1</a>', s))
    if s.startswith('http://'):
        return dict(value=s, html='<a href="%s">%s</a>' % (s,s))
    return s

def _rewrite_url(urlfield, info):
    """Set value for info[urlfield] to URL of package info['Name']."""
    try:
        package = info['Name']
    except KeyError:
        raise ValueError('Package name must be present in package info.')
    else:
        info[urlfield] = _make_link(get_base_url() +
            tg.url('/package/%s' % package))

def _xform_fieldname(s):
    """Return s with dashes repleced with spaces and ever word capitalized."""
    s = s.replace('-', ' ')
    return string.capwords(s)

def get_base_url():
    """Return base URL of application.

    Tries to account for 'Host' header and reverse proxing.

    """
    base_url =  tg.config.get('base_url_filter.base_url')
    if not base_url:
        host = cp.request.headers.get('X-Forwarded-For',
            cp.request.headers['Host'])
        if host:
            base_url =  '%s://%s' % (cp.request.scheme, host)
        else:
            base_url = cp.request.base
    return base_url

def has_extension(filename, extensions=[], case_sensitive=False):
    """Return True if filename has one of the given extensions, False otherwise.
    """
    if not case_sensitive:
        filename = filename.lower()
    for extension in extensions:
        if not case_sensitive:
            extension = extension.lower()
        if filename.endswith(extension):
            return True
    return False

def is_package_dir(path):
    """Returns True if path is a directory containing at least one package file.
    """
    if os.path.isdir(path):
        for filename in os.listdir(path):
            if is_package_file(filename):
                return True
    return False

def is_package_file(filename):
    """Return True if filename ends in one of the known package file extension.
    """
    known_extensions = tg.config.get('eggbasket.package_extensions', [])
    return has_extension(filename, known_extensions)

def munge_pkg_info(pkg_info):
    """Rewrite package info data for display on meta data view page.

    Turns URLs into links and optionall rewrites hoemapge/download URLs.

    """
    new_info = OrderedDict()
    ordered_fields = tg.config.get('eggbasket.pkg_info.sort_order', [])
    extra_fields = sorted(list(set(pkg_info.keys()).difference(ordered_fields)))
    for fieldnames in (ordered_fields, extra_fields):
        for key in fieldnames:
            if key in pkg_info:
                value = pkg_info[key]
                if not isinstance(value, list):
                    value = _make_link(value)
                new_info[_xform_fieldname(key)] = value
    if tg.config.get('eggbasket.rewrite_download_url', False):
        _rewrite_url('Download Url', new_info)
    if tg.config.get('eggbasket.rewrite_homepage_url', False):
        _rewrite_url('Home Page', new_info)
    return new_info

def txt2html(text, use_docutils=True):
    """Try to convert text into HTML with docutils.

    If conversion fails using docutils is is turned off by the configuration,
    return text unaltered.

    """
    if tg.config.get('has_docutils', False) and use_docutils:
        try:
            text = HTML(text, report_level=0, initial_header_level=2)
        except: pass
    return text
