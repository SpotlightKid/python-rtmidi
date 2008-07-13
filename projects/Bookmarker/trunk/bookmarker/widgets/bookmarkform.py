__all__ = [
  'BookmarkForm',
  'bookmarkform'
]

from turbogears import widgets
from turbogears import validators

class BookmarkForm(widgets.TableForm):
    submit = widgets.SubmitButton(attrs=dict(id='submit_bookmark'))

class BookmarkFormWidgets(widgets.WidgetsList):
    title = widgets.TextField('title',
      label=_(u'Title'), attrs=dict(maxlength=255),
      help_text=_(u'The link title. Required'))
    url = widgets.TextField('url',
      label=_(u'URL'), attrs=dict(maxlength=255),
      help_text=_(u'The URL of the bookmarked page. Required'))
    description = widgets.TextArea('description',
      label= _(u'Description'), rows=7,
      help_text=_(u'Short description of the bookmarked page. Optional'))
    tags = widgets.TextField('tags',
      label=_(u'Tags'), attrs=dict(maxlength=1000),
      help_text=_(u'A comma-separated list of tags. Optional'))

class BookmarkFormSchema(validators.Schema):
    id = validators.Int(default=None)
    title = validators.UnicodeString(not_empty=True, max=255, strip=True)
    url = validators.All(
      validators.UnicodeString(not_empty=True, max=255, strip=True),
      validators.URL(add_http=True))
    description = validators.UnicodeString(max=1000, strip=True)
    tags = validators.UnicodeString(max=1000, strip=True)

bookmarkform = BookmarkForm(
    name="bookmarkform",
    fields=BookmarkFormWidgets(),
    validator=BookmarkFormSchema())
