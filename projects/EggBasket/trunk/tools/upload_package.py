#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""A simple script to upload a package file to an EggBasket package index."""

import cookielib
import httplib
import mimetypes
import mimetools
import optparse
import os
import sys
import urllib2
import urlparse


__program__   = "upload_package.py"
__author__    = "Christopher Arndt"
__version__   = "0.1"
__revision__  = "$Rev:$"
__date__      = "$Date:$"
__copyright__ = "MIT license"
__usage__ = "%prog [-u <username> -p <password>] PACKAGE_NAME PACKAGE_FILE"

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)

def post_url(url, fields, files):
    """Post fields and files to given HTTP URL as multipart/form-data."""

    urlparts = urlparse.urlsplit(url)
    if not urlparts[0].startswith('http'):
        raise ValueError('Only HTTP URLs are supported.')
    return post_multipart(urlparts[1], urlparts[2], fields, files)

def post_multipart(host, selector, fields, files):
    """Post fields and files to an HTTP host as multipart/form-data.

    'fields' is a sequence of (name, value) elements for regular form fields.
    'files' is a sequence of (name, filename, value) elements for data to be
    uploaded as files

    Return a tuple with the response status, status message and reponse data.

    """
    content_type, body = encode_multipart_formdata(fields, files)
    h = httplib.HTTPConnection(host)
    headers = {
        'User-Agent': 'INSERT USERAGENTNAME',
        'Content-Type': content_type
        }
    h.request('POST', selector, body, headers)
    res = h.getresponse()
    return res.status, res.reason, res.read()

def encode_multipart_formdata(fields, files):
    """Encode request variables and files as a multipart/fromdata string.

    'fields' is a sequence of (name, value) elements for regular form fields.
    'files' is a sequence of (name, filename, value) elements for data to be
    uploaded as files

    Return (content_type, body) tuple, ready for use by httplib.HTTP instance.

    """
    BOUNDARY = mimetools.choose_boundary()
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' %
            (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

def post_package(name, file, username=None, password=None):
    fields = [('name', name), ('login', 'Login')]
    if username:
        fields.append(('user_name', username))
        if password:
            fields.append(('password', password))
    filedata = ('content', os.path.basename(file), open(file, 'rb').read())
    return post_url(options.url, fields, [filedata])

def main(args):
    global options, optparser

    optparser = optparse.OptionParser(prog=__program__, usage=__usage__,
      version=__version__, description=__doc__)
    optparser.add_option("-v", "--verbose",
      action="store_true", dest="verbose", default=False,
      help="Print what's going on to stdout.")
    optparser.add_option("-u", "--username",
      dest="username", help="User name to supply to the package index.")
    optparser.add_option("-p", "--password",
      dest="password", help="Password to supply to the package index.")
    optparser.add_option("-i", "--index-url",
      dest="url", help="The URL to upload the package file to.",
      default="http://tg-pypi.no-ip.org/upload")

    (options, args) = optparser.parse_args(args=args)

    if len(args) < 2:
        optparser.print_help()
        return 2
    else:
        name, file = args[:2]

    errors = []
    if os.path.exists(file):
        if options.verbose:
            print "Uploading %s..." % file
        ret = post_package(name, file, options.username, options.password)
        if ret[0] != 200:
            sys.stderr.write("Upload failed: %s - %s\n" % ret[:2])
            if options.verbose:
                sys.stderr.write("\nServer response:\n%s" % ret[2])
            return 1
    else:
        sys.stderr.write("Package file '%s' not found.\n" % file)
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
