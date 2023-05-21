#!/usr/bin/env python

import argparse
import shutil
import sys
from os import chdir, environ, getcwd
from os.path import join

from subprocess import run

build_root = environ.get("MESON_BUILD_ROOT")
dist_root = environ.get("MESON_DIST_ROOT")
source_root = environ.get("MESON_SOURCE_ROOT")
verbose = environ.get("MESON_INSTALL_QUIET") is None

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--verbose", action="store_true", default=verbose, help="Be more verbose.")
ap.add_argument("mod_source", nargs="*", help="Cython module C++ source target(s) (*.cpp).")
args = ap.parse_args()

if args.verbose:
    print("cwd:", getcwd())
    print("build root:", build_root)
    print("dist root:", dist_root)
    print("source root:", source_root)
    print("sys.argv:", sys.argv)

for mod in args.mod_source:
    target = join("src", mod)
    dst = join(dist_root, "src", mod)

    if args.verbose:
        print("Updating Cython module C source '{}'...".format(target))

    cmd = ["ninja"]

    if args.verbose:
        cmd += ["-v"]

    cmd += [target]

    chdir(build_root)
    proc = run(cmd)

    if proc.returncode != 0:
        sys.exit("'ninja' returned non-zero ({}) for target '{}'.".format(proc.returncode, target))

    shutil.copy(target, dst)
