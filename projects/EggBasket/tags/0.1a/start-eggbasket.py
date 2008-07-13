#!/home/chris/lib/tg11py25/bin/python
# -*- coding: utf-8 -*-
"""Start script for the EggBasket TurboGears project.

This script is only needed during development for running from the project
directory. When the project is installed, easy_install will create a
proper start script.
"""

import sys
from eggbasket.commands import main, ConfigurationError

if __name__ == "__main__":
    try:
        main()
    except ConfigurationError, exc:
        sys.stderr.write(str(exc))
        sys.exit(1)
