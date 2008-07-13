# -*- coding: UTF-8 -*-
"""Helper functions for handling package meta data."""

__all__ = [
    'parse_pkg_info',
    'read_pkg_info'
    'read_pkg_info_from_egg',
    'read_pkg_info_from_tar'
]

import logging
import re
import sys
import tarfile
import zipfile

from os.path import isdir, join

from eggbasket.util import has_extension


_line_rx = re.compile(r'^([\w-]+?):\s?(.*)')
log = logging.getLogger("eggbasket.controllers")


class ParseError(Exception):
    pass
class UnsupportedFormatError(Exception):
    pass

def _to_unicode(s):
    """Convert string to unicode by assuming ISO-8859-15 encoding."""
    try:
        return unicode(s, 'iso-8859-15')
    except UnicodeDecodeError:
        return unicode(s, 'utf-8')

def read_pkg_info_from_tar(filename):
    """Read PKG-INFO file from (compresse/gzipped/bzipped) tar file."""
    if not tarfile.is_tarfile(filename):
        raise UnsupportedFormatError("Unsupported tar file")
    tar = tarfile.open(filename)
    try:
        # get path of PKG-INFO file in archive
        pkg_info_filename = (i.name for i in tar
            if i.name.endswith('egg-info/PKG-INFO')).next()
        fo = tar.extractfile(pkg_info_filename)
    except (StopIteration, tarfile.TarError), exc:
        raise UnsupportedFormatError("Can't read PKG-INFO from '%s'." % filename)
    else:
        pkg_info_src = fo.read()
    fo.close()
    tar.close()

    return pkg_info_src

def read_pkg_info_from_egg(filename):
    """Read PKG-INFO file from Python egg file or directory."""
    if isdir(filename):
        pkg = open(join(filename, 'EGG-INFO', 'PKG-INFO'))
        pkg_info_src = fo.read()
    else:
        try:
            pkg = zipfile.ZipFile(filename, 'r')
        except zipfile.error:
            raise IOError("Can't read egg/zip file '%s'." % filename)
        else:
            try:
                pkg_info_filename = (name for name in pkg.namelist()
                    if name.endswith('/PKG-INFO')).next()
                pkg_info_src = pkg.read(pkg_info_filename)
            except (StopIteration, zipfile.error), exc:
                raise UnsupportedFormatError(
                    "Can't read PKG-INFO from '%s'." % filename)
    pkg.close()

    return pkg_info_src

def set_pkg_info_field(pkg_info, field, value):
    """Sets field value in pkg_info.

    If field is already set, value will be a list of all values.

    """
    if field in pkg_info:
        if not isinstance(pkg_info[field], list):
            pkg_info[field] = [pkg_info[field]]
        pkg_info[field].append(value)
    else:
        pkg_info[field] = value

def parse_pkg_info(pkg_info_src):
    """Parse string with PKG-INFO meta data.

    Returns dictionary with PKG-INFO fields as keys. Mutiple field values
    are collected in a list value.

    Raises ParseError on any malformatted line.

    """
    lines = pkg_info_src.split('\n')
    pkg_info = dict()
    field = None
    value = ''

    for i, line in enumerate(lines):
        if line and line[0] in [' ', '\t']:
            # continuation line
            if field:
                value += '\n' + line.strip()
            else:
                raise ParseError('Misplaced continuation line: %s' % line)
        else:
            if not line.strip():
                # empty line
                continue
            mo = _line_rx.match(line)
            if mo:
                # new field -> set accumulated value for previous field
                if field:
                    set_pkg_info_field(pkg_info, field, value)
                field = mo.group(1).lower()
                value = _to_unicode(mo.group(2).strip())
            else:
                # invalid line format
                raise ParseError('Invalid PKG-INFO line: %s' % line)
    else:
        set_pkg_info_field(pkg_info, field, value)
    return pkg_info

def read_pkg_info(filename):
    """Read PKG-INFO meta data from given package distribution file.

    If the package file format is not supported, returns empty dict.

    See parse_pkg_info() for more information.

    """
    try:
        if has_extension(filename, ('.egg', '.zip')):
            pkg_info_src = read_pkg_info_from_egg(filename)
        elif has_extension(filename,
            ('.tar', 'tar.bz2', 'tar.gz', 'tar.Z', '.tgz')):
            pkg_info_src = read_pkg_info_from_tar(filename)
        else:
            raise UnsupportedFormatError
    except (IOError, OSError, ParseError, UnsupportedFormatError), exc:
        log.warning("Could not read PKG-INFO from file '%s': %s", filename, exc)
        return dict()
    else:
        return parse_pkg_info(pkg_info_src)

if __name__ == '__main__':
    import pprint
    pprint.pprint(parse_pkg_info(read_pkg_info_from_egg(sys.argv[1])))
