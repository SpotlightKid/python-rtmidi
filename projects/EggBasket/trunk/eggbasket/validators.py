# -*- coding: UTF-8 -*-

import os

from os.path import exists, join

import turbogears as tg

from eggbasket.util import is_package_dir, is_package_file

class ValidPackage(tg.validators.FancyValidator):
    """Validator checking if a package name refers to a valid package directory.
    """

    messages = {
      'notFound': u'Package not found: %(package)s'
    }

    def _to_python(self, value, state):
        pkg_root = tg.config.get('eggbasket.package_root', os.getcwd())
        if not is_package_dir(join(pkg_root, value)):
            # WART: to handle broken package names,
            # we also try the given package name in lowercase
            if is_package_dir(join(pkg_root, value.lower())):
                value = value.lower()
            else:
                raise tg.validators.Invalid(
                    self.message('notFound', state, package=value), value, state)
        return value

class ValidPackageFile(tg.validators.FancyValidator):
    """Validator checking if a file name refers to a valid package file.

    Must be used as a chained validator.
    """

    messages = {
      'notFound': u'Package file not found: %(filename)s'
    }

    def validate_python(self, value, state):
        filename = value['filename']
        pkg_root = tg.config.get('eggbasket.package_root', os.getcwd())
        pkg_dir = join(pkg_root, value['package'])
        pkg_file = join(pkg_dir, filename)
        if not exists(pkg_file) or not is_package_file(pkg_file):
            message = self.message('notFound', state, filename=filename)
            errors = dict(filename=message)
            raise tg.validators.Invalid(message, value, state,
                error_dict=errors)

class PackageFileSchema(tg.validators.Schema):
    """Schema for package file spec consisting of package and file name."""

    package = ValidPackage
    filename = tg.validators.UnicodeString

    chained_validators = [ValidPackageFile]

__all__ = [
    'PackageFileSchema'
    'ValidPackage',
    'ValidPackageFile'
]
