FancyFlashExample
=================

:Author: Christopher Arndt
:Version: 1.0
:Date: $Date$
:Copyright: MIT License


This is a little TurboGears_ project demonstrating the TurboFancyFlash_
extension. TurboFancyFlash is a (drop-in) replacement / enhancement for the 
``turbogears.flash()`` function, providing much nicer-looking message boxes 
that can change their appearance based on the status of the message.

Installation
------------

To install the FancyFlashExample_ application you can use `easy_install`_::

    [sudo] easy_install -f http://chrisarndt.de/projects/fancyflash/ \
        FancyFlashExample

This requires the setuptools_ package to be installed. If you have not done so
already, download the `ez_setup.py`_ script and run it to install setuptools.

You can also download one of the following packages and install them manually:

* `Tar/Bzip2 source package <FancyFlashExample-1.0.tar.bz2>`_
* `ZIP source package <FancyFlashExample-1.0.zip>`_
* Platform-independant `Python 2.5 egg <FancyFlashExample-1.0-py25.egg>`_


Usage
-----

You can start the application by running the ``start-fflashex`` script which
will be installed with the application. Then open your web browser at
``http://localhost:8080/``.


.. _turbogears: http://www.turbogears.org/
.. _turbofancyflash: http://chrisarndt.de/projects/fancyflash/
.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools
.. _easy_install: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _ez_setup.py: http://peak.telecommunity.com/dist/ez_setup.py
