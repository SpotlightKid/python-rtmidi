# -*- coding: UTF-8 -*-

# standard library imports
import logging
import os

from os.path import dirname, exists, isdir, join
from operator import attrgetter

# third-party library imports
import cherrypy as cp
import turbogears as tg

from cherrypy.lib.cptools import serve_file

# private modules
from eggbasket import model
from eggbasket.validators import ValidPackage, PackageFileSchema
from eggbasket.util import is_package_dir, munge_pkg_info, txt2html
from eggbasket.permissions import has_permission

log = logging.getLogger("eggbasket.controllers")

class PackageController(tg.controllers.Controller):
    """Controller for handling package info display, download and upload."""

    @tg.expose(template="eggbasket.templates.package_list")
    @tg.identity.require(has_permission(u'viewpkgs',
        u'You have no permission to view the list of packages.'))
    def index(self, *args, **kw):
        """Return list of packages in the repository."""

        pkg_root = tg.config.get('eggbasket.package_root', os.getcwd())
        log.debug("Listing package root directory: %s", pkg_root)
        packages = [model.Package(join(pkg_root, name))
            for name in os.listdir(pkg_root)
            if is_package_dir(join(pkg_root, name))]
        packages.sort(key=attrgetter('name'))
        #log.debug("Packages found: %r", packages)

        return dict(packages=packages)

    @tg.expose("eggbasket.templates.package_files")
    @tg.validate(validators=dict(package=ValidPackage))
    @tg.identity.require(has_permission(u'viewfiles',
        u'You have no permission to view package distibution file lists.'))
    def files(self, package, tg_errors=None):
        """List available releases and distribution files for given package."""
        if tg_errors:
            # Send 404 for unavailable packages, to not confuse easy_install
            raise cp.NotFound()
            # XXX: I should test if it's ok to do the following instead:
            #tg.flash(unicode(tg_errors['package']))
            #tg.redirect('/')

        pkg_root = tg.config.get('eggbasket.package_root', os.getcwd())
        pkg_dir = join(pkg_root, package)
        log.debug("Reading package directory %s.", pkg_dir)
        package = model.Package(pkg_dir)
        return dict(package=package)

    default = files

    @tg.expose('eggbasket.templates.package_info')
    @tg.validate(validators=PackageFileSchema)
    @tg.identity.require(has_permission(u'viewinfo',
        u'You have no permission to view package meta data.'))
    def info(self, package, filename, tg_errors=None):
        """Show meta data from PKG-INFO for given package distribution file."""
        if tg_errors:
            if tg_errors.get('package'):
                tg.redirect('/')
                flash(unicode(tg_errors['package']))
            if tg_errors.get('filename'):
                flash(unicode(tg_errors['filename']))
                tg.redirect('/package/%s' % package)

        pkg_root = tg.config.get('eggbasket.package_root', os.getcwd())
        pkg_dir = join(pkg_root, package)
        package = model.Package(pkg_dir)
        pkg_info = package.package_info(join(pkg_dir, filename))
        pkg_desc = txt2html(pkg_info.pop('description', ''),
            tg.config.get('eggbasket.pkg_desc_format', 'plain') == 'rest')
        pkg_info = munge_pkg_info(pkg_info)
        return dict(package=package, description=pkg_desc, pkg_info=pkg_info,
            filename=filename)

    @tg.expose()
    @tg.validate(validators=PackageFileSchema)
    @tg.identity.require(has_permission(u'download',
        u'You have no permission to download package distribution files.'))
    def download(self, package, filename, tg_errors=None):
        """Serve given package distribution file as binary download."""
        if tg_errors:
            if tg_errors.get('package'):
                tg.redirect('/')
                flash(unicode(tg_errors['package']))
            if tg_errors.get('filename'):
                flash(unicode(tg_errors['filename']))
                tg.redirect('/package/%s' % package)

        pkg_root = tg.config.get('eggbasket.package_root', os.getcwd())
        pkg_file = join(pkg_root, package, filename)
        return serve_file(pkg_file, "application/octet-stream",
            "attachment", filename)

    @tg.expose()
    def upload(self, name, content, *args, **kw):
        """Handle submissions from the distutils 'upload' command."""
        # We don't use the identity.require decorator, since we don't want to
        # return the login form on an authentication error here.
        if not has_permission('upload'):
            # User does not have 'upload' permission
            raise cp.HTTPError(401, "Unauthorized - No upload permission")

        pkg_root = tg.config.get('eggbasket.package_root', os.getcwd())
        pkg_dir = join(pkg_root, name)
        pkg_file = os.path.join(pkg_dir, content.filename)
        if exists(pkg_file) and not has_permission('overwrite'):
            # File exists: return standard HTTP status code 409
            raise cp.HTTPError(409, "Conflict - File exists")

        # create package directory, if it does not exist
        if not isdir(pkg_dir):
            try:
                os.makedirs(pkg_dir)
            except (IOError, OSError), exc:
                # Directory cannot be created
                log.error("Could not create package directory '%s': %s",
                    pkg_dir, exc)
                raise cp.HTTPError(500, "Internal Server Error"
                   " - Could not create package directory")

        # write uploaded package to file
        try:
            fo = open(pkg_file, 'wb')
            try:
                while True:
                    chunk = content.file.read(8192)
                    if not chunk:
                        break
                    fo.write(chunk)
            finally:
                fo.close()
        except (IOError, OSError), exc:
            # Package file not writeable
            log.error("Could not write package file '%s': %s",
                pkg_file, exc)
            raise cp.HTTPError(500, "Internal Server Error"
               " - Could not write package file")
        log.info('Uploaded %s' % pkg_file)
        return ""


    @tg.expose()
    @tg.validate(validators=PackageFileSchema)
    @tg.identity.require(has_permission(u'delete',
        u'You have no permission to delete package distribution files.'))
    def delete(self, package, filename, tg_errors=None):
        """Delete a package file from the repository."""

        if tg_errors:
            if tg_errors.get('package'):
                tg.redirect('/')
                flash(unicode(tg_errors['package']))
            if tg_errors.get('filename'):
                flash(unicode(tg_errors['filename']))
                tg.redirect('/package/%s' % package)
        pkg_root = tg.config.get('eggbasket.package_root', os.getcwd())
        pkg_file = join(pkg_root, package, filename)
        try:
            os.unlink(pkg_file)
            tg.flash(u"Package file '%s' deleted." % filename)
        except OSError, exc:
            tg.flash(u"Could not delete package file '%s': %s" % (
                filename, exc))
        if is_package_dir(join(pkg_root, package)):
            tg.redirect('/package/%s' % package)
        else:
            tg.redirect('/')

