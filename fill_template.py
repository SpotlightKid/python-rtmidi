#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Custom distutils command to fill placeholders in text files with release
meta-data.

"""

from os.path import join
from string import Template

try:
    basestring  # noqa
except:
    basestring = str

from distutils.core import Command
from distutils.dist import DistributionMetadata
from distutils.log import error, info
from distutils.util import split_quoted


DistributionMetadata.templates = None


class FillTemplate(Command):
    """Custom distutils command to fill text templates with release meta data.
    """

    description = "Fill placeholders in documentation text file templates"

    user_options = [
        ('templates=', None, "Template text files to fill")
    ]

    def initialize_options(self):
        self.templates = ''
        self.template_ext = '.in'

    def finalize_options(self):
        if isinstance(self.templates, basestring):
            self.templates = split_quoted(self.templates)

        self.templates += getattr(self.distribution.metadata, 'templates', None) or []

        for tmpl in self.templates:
            if not tmpl.endswith(self.template_ext):
                raise ValueError("Template file '%s' does not have expected "
                                 "extension '%s'." % (tmpl, self.template_ext))

    def run(self):
        metadata = self.get_metadata()

        for infilename in self.templates:
            try:
                info("Reading template '%s'...", infilename)
                with open(infilename) as infile:
                    tmpl = Template(infile.read())
                    outfilename = infilename.rstrip(self.template_ext)

                    info("Writing filled template to '%s'.", outfilename)
                    with open(outfilename, 'w') as outfile:
                        outfile.write(tmpl.safe_substitute(metadata))
            except:
                error("Could not open template '%s'.", infilename)

    def get_metadata(self):
        data = dict()
        for attr in self.distribution.metadata.__dict__:
            if not callable(attr):
                data[attr] = getattr(self.distribution.metadata, attr)

        data['cpp_info'] = open(join("src", '_rtmidi.cpp')).readline().strip()
        return data
