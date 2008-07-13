__all__ = [
  'events',
  'mochikit'
]

import pkg_resources
from turbogears.widgets import JSLink, register_static_directory

js_dir = pkg_resources.resource_filename("cblog.widgets.jslibs",
  "static")
register_static_directory("jslibs", js_dir)

mochikit = JSLink("jslibs", "javascript/MochiKit.js")
events = JSLink("jslibs", "javascript/events.js")
