#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fill placeholders in text file with release data."""

import os
import sys
import time

from os.path import join

try:
    basestring
except:
    basestring = str

from setuptools import Command
from distutils.log import error, info
from distutils.util import split_quoted

def get_setup_opts():
    setup_opts = {}
    release_info = join("rtmidi", 'release.py')
    exec(compile(open(release_info).read(), release_info, 'exec'), {}, setup_opts)
    setup_opts['cpp_info'] = open(join("src", '_rtmidi.cpp')).readline().strip()
    return setup_opts

class FillTemplate(Command):
    """Custom distutils command to fill text templates with release meta data.
    """

    description = "Fills placeholders in documentation text file templates"

    user_options = [
        ('templates=', None, "Template text files to fill")
    ]

    def initialize_options(self):
        self.templates = ''
        self.template_ext = '.in'

    def finalize_options(self):
        if isinstance(self.templates, basestring):
            self.templates = split_quoted(self.templates)

        for tmpl in self.templates:
            if not tmpl.endswith(self.template_ext):
                raise ValueError("Template file '%s' does not have expected "
                    "extension '%s'." % (tmpl, self.template_ext))

    def run(self):
        setup_opts = get_setup_opts()
        for infilename in self.templates:
            info("Reading template '%s'...", infilename)
            try:
                with open(infilename) as infile:
                    outfilename = infilename.rstrip(self.template_ext)
                    info("Writing filled template to '%s'.", outfilename)
                    with open(outfilename, 'w') as outfile:
                        outfile.write(infile.read() % setup_opts)
            except:
                error("Could not open template '%s'.", infilename)
