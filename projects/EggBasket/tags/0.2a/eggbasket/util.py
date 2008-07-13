# -*- coding: UTF-8 -*-

import os
import re
import string

import turbogears as tg

try:
    from eggbasket.rest import HTML
    tg.config.update({'has_docutils': True})
except ImportError:
    tg.config.update({'has_docutils': False,
        'eggbasket.pkg_desc_format': 'plain'})


def _xform_fieldname(s):
    s = s.replace('-', ' ')
    return string.capwords(s)

_email_rx = re.compile(r'([-\w.+]+@[\w.]+?\.\w+)')
def make_link(s):
    if _email_rx.search(s):
        return dict(value=s,
            html=_email_rx.sub(r'<a href="mailto:\1">\1</a>', s))
    if s.startswith('http://'):
        return dict(value=s, html='<a href="%s">%s</a>' % (s,s))
    return s

def munge_pkg_info(pkg_info):
    new_info = []
    ordered_fields = tg.config.get('eggbasket.pkg_info.sort_order', [])
    extra_fields = sorted(list(set(pkg_info.keys()).difference(ordered_fields)))
    for fieldnames in (ordered_fields, extra_fields):
        for key in fieldnames:
            if key in pkg_info:
                value = pkg_info[key]
                if not isinstance(value, list):
                    value = make_link(value)
                new_info.append((_xform_fieldname(key), value))
    return new_info

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

def is_package_file(filename):
    """Return True if filename ends in one of the known package file extension.
    """
    known_extensions = tg.config.get('eggbasket.package_extensions', [])
    return has_extension(filename, known_extensions)

def is_package_dir(path):
    """Returns True if path is a directory containing at least one package file.
    """
    if os.path.isdir(path):
        for filename in os.listdir(path):
            if is_package_file(filename):
                return True
    return False

def txt2html(text, use_docutils=True):
    if tg.config.get('has_docutils', False) and use_docutils:
        try:
            text = HTML(text, report_level=0, initial_header_level=2)
        except: pass
    return text

__all__ = [
    'has_extension',
    'is_package_dir',
    'is_package_file',
    'munge_pkg_info',
    'txt2html',
]
