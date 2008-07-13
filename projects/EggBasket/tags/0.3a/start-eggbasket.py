#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Start script for the EggBasket TurboGears project.

This script is only needed during development for running from the project
directory. When the project is installed, easy_install will create a
proper start script.
"""

import sys

from os.path import abspath, exists, join

# look for virtual environment in current dir
# if there is one, activate it.
ve_dir = 'tgenv'
if exists(join(ve_dir, 'bin', 'activate')) or \
  exists(join(ve_dir, 'Scripts', 'activate.bat')):
    import site
    py_maj_ver = "%i.%i" % sys.version_info[:2]
    site.addsitedir(join(ve_dir, 'lib', 'python%s' % py_maj_ver,
        'site-packages'))

from eggbasket.commands import main, ConfigurationError

if __name__ == "__main__":
    try:
        main()
    except ConfigurationError, exc:
        sys.stderr.write(str(exc))
        sys.exit(1)
