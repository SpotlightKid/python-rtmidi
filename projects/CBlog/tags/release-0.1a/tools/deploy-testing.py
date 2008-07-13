#!/usr/bin/env python

import os
import sys

# !!!Change these settings to match you environment!!!
SUPERVISOR_PORT = 9001
APP_NAME = PKG_NAME = 'cblog'
RMT_DIR = 'share/tg_apps'
DST = "ca@rainbow:"

try:
    DST = sys.argv.pop(1)
except IndexError:
    pass

if not ':' in DST:
    DST = DST.rstrip('/') + '/'
DST_DIR = '%s%s' % (DST, RMT_DIR)

try:
    SRC = os.path.abspath(sys.argv.pop(1))
except IndexError:
    SRC = os.getcwd()

EXCLUDES = ['*.py', '*.py.bak', '*data/*', 'misc', 'tools', '*.log', 'doc',
  '.svn', '*.egg-info', 'dist', 'build', 'sqlobject-history/*',
  'catwalk-session/*', 'setup.py', 'dev.cfg', 'README*', 'MANIFEST*']

INCLUDES = ['start-%s.py' % PKG_NAME]

# re-compile templates
os.system('cheetah-autocompile %s/templates 0' % PKG_NAME)

# update *.pyc files
os.system('python -m compileall %s' % PKG_NAME)

if ':' in DST:
    os.system('ssh-add -l | grep -q "$HOME/.ssh/id_dsa" || ssh-add')

EXCLUDE_OPTS = "".join((" '--exclude=%s'" % ex for ex in EXCLUDES))
INCLUDE_OPTS = "".join((" '--include=%s'" % incl for incl in INCLUDES))

cmd = 'rsync -av --update %s %s "%s" "%s"' % \
  (EXCLUDE_OPTS, INCLUDE_OPTS, SRC, DST_DIR)
print cmd
os.system(cmd)

# restart server
if ':' in DST:
    os.system('supervisorctl -s http://%s:%i restart %s' % \
      (DST.split(':', 1)[0], SUPERVISOR_PORT, APP_NAME))
else:
    os.system('supervisorctl restart %s' % APP_NAME)
