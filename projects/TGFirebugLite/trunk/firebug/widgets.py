__all__ = [
    'firebug_css',
    'firebug_js',
    'firebugx_js'
]

import pkg_resources

from turbogears.widgets import CSSLink, JSLink, Widget, WidgetDescription, \
                               register_static_directory

static_dir = pkg_resources.resource_filename("firebug", "static")
register_static_directory("firebug", static_dir)

firebug_css = CSSLink("firebug", "css/firebug.css")
firebug_js = JSLink("firebug", "javascript/firebug.js")
firebugx_js = JSLink("firebug", "javascript/firebugx.js")
