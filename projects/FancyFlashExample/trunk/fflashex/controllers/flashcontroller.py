# -*- coding: UTF-8 -*-

from pprint import pformat

# third party modules
from turbogears import controllers, expose, flash, redirect, url, validate, \
  validators, view
from turbogears.widgets import JSSource, js_location

# own modules
from fancyflash import *

# global settings
set_default_flash_timeout(10)
register_flash_widget()

def add_pformat(variables):
    variables["pformat"] = pformat

# Uncomment following line to display template variables one each page
#view.variable_providers.append(add_pformat)

class FlashTestController(controllers.Controller):
    
    onclick_tmpl = """\
    connect('fancy_%(stat)s', 'onclick',
        function() {
            displayStatusMessage($('te_msg').value, '%(stat)s', 5);
        }
    );
    """

    html_message = """\
    <h3>A little heading</h3>

    <p>This is the first pararagh.</p>

    <p>And here comes a second.</p>
    """

    @expose(template="fflashex.templates.welcome")
    def index(self):
        context = dict()
        for stat in ['info', 'warning', 'error', 'success']:
            context[stat] = JSSource(self.onclick_tmpl % {'stat': stat},
                location=js_location.bodybottom)
        return context

    @expose()
    def flash(self):
        flash("We are backwards compatible!")
        redirect('/')

    @expose()
    @validate(validators=dict(timeout=validators.Int))
    def info(self, timeout=0, tg_errors=None):
        info("You have made a simple controller happy! Share & enjoy! "
          "Standby...", timeout)
        redirect('/')

    @expose()
    @validate(validators=dict(timeout=validators.Int))
    def error(self, timeout=0, tg_errors=None):
        error("HTML is turned <em>off</em> by default!", timeout)
        redirect('/')

    @expose()
    @validate(validators=dict(timeout=validators.Int))
    def warning(self, timeout=0, tg_errors=None):
        warning("Do not click this link again!", timeout)
        redirect('/')

    @expose()
    @validate(validators=dict(timeout=validators.Int))
    def success(self, timeout=0, tg_errors=None):
        success(u"¡Si, Señor!", timeout)
        redirect('/')

    @expose()
    @validate(validators=dict(timeout=validators.Int, status=validators.String))
    def showoff(self, status="info", timeout=0, tg_errors=None):
        statusmessage(self.html_message, status, timeout, allow_html=True)
        redirect('/')

