# Release information about TurboFancyFlash
# -*- coding: UTF-8 -*-
"""TurboGears extension providing enhanced flash message display functions.

This package provides an enhanced version of the ``turbogears.flash()``
function, giving your users much nicer-looking message boxes that can change 
their appearance based on the status of the message. With JavaScript enabled,
messages can fade out after a timeout or be dismissed by the user with a 
mouse-click.

This is accomplished by encoding the message with JSON and decoding it again in 
the template of the target page. This is handled completely automatic and the 
programmer can just use the functional interface, e.g. 
``fancyflash.error("Duh!")``.

Additionally, you can display messages with a simple JavaScript function call, for example when processing the results of an AJAX call in your callback function for ``loadJSONDoc``.

For more information see the source of the ``fancyflash`` package, the 
epydoc-generated `API documentation`_ and the FancyFlashExample_ application.


Installation
------------

To install TurboFancyFlash from the Cheeseshop_ use `easy_install`_::

    [sudo] easy_install TurboFancyFlash

This requires the setuptools_ package to be installed. If you have not done so
already, download the `ez_setup.py`_ script and run it to install setuptools.


Usage
-----

Controller (``controllers.py``)::

    # Import TurboGears
    from turbogears import controllers, expose, redirect, validate, validators

    # Import fancyflash package
    import fancyflash as ff

    # Set the default timeout for message box display
    ff.set_default_flash_timeout(5)

    # Let FancyFlashWidget be included on every page
    ff.register_flash_widget()

    class FlashTestController(controllers.Controller):

        @expose('templates.welcome')
        def index(self, timeout=0):
            return {}

        @expose()
        def info(self):
            ff.info("Hello TurboGears!")
            redirect('/')

        @expose()
        @validate(validators=dict(timeout=validators.Int))
        def success(self, timeout=0, tg_errors=None):
            ff.success("Hello TurboGears!", timeout)
            redirect('/')

        @expose()
        @validate(validators=dict(status=validators.String))
        def message(self, status="info", tg_errors=None):
            ff.statusmessage("Hello TurboGears!", status)
            redirect('/')

Master template (``master.kid``)::

    <div id="main_content">
      <div py:replace="tg_fancyflashwidget(tg_flash)">Status message
        appears here</div>

      <div py:replace="[item.text]+item[:]"/>
    
      ...
    </div>


Acknowledgments
---------------

The idea for this widget is based on a `blog post`_ by Lee McFadden:

.. _blog post:
    http://www.splee.co.uk/2005/11/23/fancy-status-messages-using-tg_flash/


Todo
----

* Test in IE
* Test opacity in Safari

If I have time:

* Add argument for dialog position (implement by writing CSS dynamically).
* Round boxes for non-Gecko browsers
* Add AJAX widget, which displays result of ``loadJSONDoc`` as fancy status 
  message.

.. _api documentation:
    http://chrisarndt.de/projects/fancyflash/api/index.html
.. _fancyflashexample: http://chrisarndt.de/projects/fancyflashexample/
.. _cheeseshop: http://cheeseshop.python.org/pypi/TurboFancyFlash
.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools
.. _easy_install: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _ez_setup.py: http://peak.telecommunity.com/dist/ez_setup.py
"""
__docformat__ = 'restructuredtext'

name = "TurboFancyFlash"
version = "0.1a"
date = "$Date$"

_doclines = __doc__.split('\n')
description = _doclines[0]
long_description = '\n'.join(_doclines[2:])

author = "Christopher Arndt"
author_email = "chris@chrisarndt.de"
copyright = "(c) 2006-2008 Christopher Arndt"
license = "MIT license"

url = "http://chrisarndt.de/projects/fancyflash/"
download_url = "http://cheeseshop.python.org/pypi/%s" % version
