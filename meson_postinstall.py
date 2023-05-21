#!/usr/bin/env python3

import sysconfig
from compileall import compile_dir
from os import environ, path

destdir = environ.get('MESON_INSTALL_DESTDIR_PREFIX', '')
verbose = environ.get("MESON_INSTALL_QUIET") is None

if verbose:
    print('Compiling Python module to bytecode...')

moduledir = sysconfig.get_path('purelib', vars={'base': destdir})
compile_dir(path.join(moduledir, 'rtmidi'), optimize=1)
