#!/usr/bin/env python
"""Create a virtualenv bootstrap script for EggBasket.

See http://pypi.python.org/pypi/virtualenv for more information.
"""

import virtualenv, textwrap

output = virtualenv.create_bootstrap_script(textwrap.dedent("""
def after_install(options, home_dir):
    subprocess.call([join(home_dir, 'bin', 'easy_install'),
        'EggBasket'])
    subprocess.call([join(home_dir, 'bin', 'eggbasket-server'), '--init'])
"""))
f = open('eggbasket-bootstrap.py', 'w').write(output)
