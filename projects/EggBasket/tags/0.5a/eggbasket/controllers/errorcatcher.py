"""TurboGears root controller base class catching errors, displaying custom error pages and sending email notifications."""
# -*- coding: UTF-8 -*-
# errorhandling.py

import datetime
import logging
import socket
import StringIO
import traceback

import cherrypy
from turbogears import config, controllers, identity, util

try:
    import turbomail
    has_turbomail = True
except ImportError:
    has_turbomail = False
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.Utils import formatdate

__all__ = ['ErrorCatcher']

log = logging.getLogger("turbogears.controllers")


def format_request_info(req):
    """Return string with formatted info about important request properties."""
    data = []
    for key in ['remote_host', 'remote_addr', 'remote_port', 'requestLine',
      'protocol', 'method', 'query_string', 'browser_url', 'body']:
        value = getattr(req, key, None)
        if value:
            data.append(u'%s: %r' % (key, value))
    return u'\n'.join(data)

def format_request_headers(req):
    """Return string with formatted request headers."""
    data = []
    for key, value in req.header_list:
        data.append(u'%s: %r' % (key, value))
    return u'\n'.join(data)

def format_user_info(user):
    """Return string with formatted info about request user."""
    data = []
    if user:
        for key in ['user_id', 'user_name', 'display_name', 'email_address']:
            value = getattr(user, key, None)
            if value:
                data.append(u'%s: %r' % (key, value))
    else:
        data.append(u'Anonymous user')
    return u'\n'.join(data)

class ErrorCatcher(controllers.RootController):
    """Base class for root controllers catching errors and showing error page.

    To use enable custom error pages, the root controller must subclass the
    ``ErrorCatcher`` class and the CherryPy filter hook must be enabled by
    setting ``error_catcher.on = True`` in the deployment configuration.

    When the error catcher is enabled and an HTML error (including an
    unhandled exception) occurs in the controller, an error page is displayed
    using a template, whose name is looked up in the ``_error_page_templates``
    class attribute by the HTML status code.

    Currently, there are default templates for the status codes 401, 403 and
    404, called ``401_error``, ``403_error`` and ``404_error`` resp. and
    ``unhandled_exception`` for all other errors. The templates are searched
    in the ``templates`` sub-package of the application.

    Also, if ``mail.on`` is ``True`` sends an email to the admin,
    when an error occurs. No email is sent if the HTML status code is
    contained in the list set by the option ``error_catcher.no_email_on``.
    The default is not to send emails for 401, 403 and 404 errors.

    For email sending to work, at least the configuration options
    'error_catcher.sender_email' and 'error_catcher.admin_email' must be
    set to valid email addresses.

    See the docstring for the method 'send_exception_email' for more email
    related configuration information.

    """
    _error_codes = {
        None: u'Unknown Error',
        400: u'400 - Bad Request',
        401: u'401 - Unauthorized',
        403: u'403 - Forbidden',
        404: u'404 - Not Found',
        500: u'500 - Internal Server Error',
        501: u'501 - Not Implemented',
        502: u'502 - Bad Gateway',
    }
    _error_page_templates = {
        None: '.templates.unhandled_exception',
        401: '.templates.401_error',
        403: '.templates.403_error',
        404: '.templates.404_error',
    }
    _error_mail_templates = {
        None: 'cheetah:.templates.email_unhandled_exception',
    }
    admin_group_name = 'admin'

    def __init__(self, *args, **kw):
        super(ErrorCatcher, self).__init__(*args, **kw)
        self.sender_email = config.get('error_catcher.sender_email')
        self.admin_email = config.get('error_catcher.admin_email')
        self.smtp_server = config.get('mail.server', 'localhost')
        self.smtp_username = config.get('mail.username')
        self.smtp_password = config.get('mail.password')
        self.no_email_on = config.get('error_catcher.no_email_on',
            (401, 403, 404))

    def cp_on_http_error(self, status, message):
        """Handle HTTP errors by sending an error page and email."""
        try:
            cherrypy._cputil._cp_on_http_error(status, message)
            error_msg = self._get_error_message(status, message)
            url = cherrypy.request.requestLine
            log.exception("CherryPy %s error (%s) for request '%s'", status,
              error_msg, url)

            # get exception traceback
            buf = StringIO.StringIO()
            traceback.print_exc(file=buf)
            exc_traceback = buf.getvalue()
            buf.close()

            # get request info
            req = cherrypy.request
            data = dict(
                error_msg = error_msg,
                header_info = format_request_headers(req),
                is_admin = identity.in_group(self.admin_group_name),
                message = message,
                request_info = format_request_info(req),
                server = req.headers.get('host', socket.getfqdn()),
                status = status,
                url = url,
                timestamp = datetime.datetime.now(),
                traceback = exc_traceback,
                user_info = format_user_info(identity.current.user),
            )

            if config.get('mail.on') and status not in self.no_email_on:
                try:
                    self.send_exception_email(**data)
                    data['email_sent'] = True
                except Exception, exc:
                    log.exception('Error email failed: %s', exc)
                    data['email_sent'] = False
            else:
                data['email_sent'] = False

            self.send_error_page(**data)
        # don't catch SystemExit
        except StandardError, exc:
            log.exception('Error handler failed: %s', exc)

    # Hook in error handler if enabled in configuration
    if config.get('error_catcher.on', False):
        _cp_on_http_error = cp_on_http_error

    def send_error_page(self, **data):
        """Render error page using template looked up in self._error_templates.
        """
        template = self._error_page_templates.get(data['status'],
            self._error_page_templates.get(None))
        body = self._render_error_template(template, data=data)
        cherrypy.response.headers['Content-Length'] = len(body)
        cherrypy.response.body = body

    def send_exception_email(self, **data):
        """Send an email with the error info to the admin.

        Uses TurboMail if installed and activated, otherwise tries to send
        email with the ``smtplib`` module. The SMTP settings can be configured
        with the following settings:

        ``mail.server``   - Mail server to connect to (default 'localhost').
        ``mail.username`` - User name for SMTP authentication. If the value
                            is unset or evaluates to False no SMTP login is
                            performed.
        ``mail.password`` - Password for SMTP authentication. may be an empty
                            string.

        See also the class docstring for information on setting the
        sender and recipient address.

        """
        if not self.sender_email or not self.admin_email:
            msg = ('Configuration error: could not send error notification '
              'because sender and/or admin email address is not set.')
            log.exception(msg)
            raise RuntimeError(msg)

        template = self._error_mail_templates.get(data['status'],
            self._error_mail_templates.get(None))
        subject =  '%(status)s ERROR on server %(server)s' % data
        body = self._render_error_template(template, 'plain', 'text/plain',
            data)

        if has_turbomail:
            msg = turbomail.Message(
                self.sender_email, self.admin_email, subject)
            msg.plain = body
            turbomail.enqueue(msg)
        else:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.admin_email
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = subject
            msg.attach(MIMEText(body))
            self._send_email_by_smtp(self.sender_email, self.admin_email,
              msg.as_string())

    def _send_email_by_smtp(self, from_addr, to_addr, message):
        """Send email via SMTP."""
        import smtplib
        smtp = smtplib.SMTP(self.smtp_server)
        if self.smtp_username and self.smtp_password is not None:
            smtp.login(self.smtp_username, self.smtp_passwordd)
        smtp.sendmail(from_addr, to_addr, message)
        smtp.close()

    def _get_error_message(self, status, default=None):
        """Return string error for HTTP status code."""
        return self._error_codes.get(status, default or self._error_codes[None])

    def _render_error_template(self, template, format='html',
            content_type='text/html', data={}):
        if ':' in template:
            prefix, template = template.split(':', 1)
            prefix += ':'
        else:
            prefix = ''
        if template.startswith('.'):
            package = util.get_package_name()
        else:
            package = ''
        template = "%s%s%s" % (prefix, package, template)
        return controllers._process_output(data, template, format,
            content_type, None)
