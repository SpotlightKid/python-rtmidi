# -*- coding: UTF-8 -*-

__all__ = [
  'archive_links', 'ArchiveLinks',
  'category_links', 'CategoryLinks',
  'events',
  'fancyflash', 'FancyFlash',
  'gravatar', 'Gravatar',
  'mochikit',
  'profile', 'Profile',
  'search_form', 'SearchForm',
  'sitewidgets'
]

import md5
from datetime import datetime

from turbogears import validators, url, config
from turbogears.widgets import *

from cblog import model
from cblog.widgets.gravatar import *
from cblog.widgets.fancyflash import *
from cblog.widgets.jslibs import *

# Widgets that shoudl be included on every page
# Order is important here for proper inclusion of JavaScript and CSS
sitewidgets = [
    'mochikit',
    'events',
    'archive_links',
    'category_links',
    'fancyflash',
    'gravatar',
    'profile',
    'search_form',
]

class Profile(Widget):
    """A profile summary to be shown in the sidebar.

    TODO:
    """

    template = """\
    <p xmlns:py="http://purl.org/kid/ns#" id="profile"></p>
    """


class ArchiveLinks(Widget):
    """A list of links to monthly archive pages."""

    params = ['archives']
    template = """\
    <ul xmlns:py="http://purl.org/kid/ns#" id="archive-links">
      <li py:for="month, entry_count in archives"><a
        href="${tg.url(month.strftime('/archive/%Y-%m'))}"
        >${month.strftime('%B %Y')} (${entry_count})</a></li>
    </ul>
    """

    def get_archives(self):
        """Assemble a list of months and number of post in each."""

        archives = {}
        for entry in model.Entry.select():
            month = entry.month
            if archives.has_key(month):
                archives[month] += 1
            else:
                archives[month] = 1
        archives = [x for x in archives.items()]
        archives.sort()
        archives.reverse()
        return archives

    def update_params(self, params):
        super(ArchiveLinks, self).update_params(params)
        params['archives'] = self.get_archives()


class CategoryLinks(Widget):
    """A list of links to posts by category."""

    params = ['tags']
    template = """\
    <ul xmlns:py="http://purl.org/kid/ns#" id="category-links">
      <li py:for="tagname, count in tags"><a
        href="${tg.url('/tag/%s' % tagname)}"
        >${tagname} (${count})</a></li>
    </ul>
    """

    def update_params(self, params):
        super(CategoryLinks, self).update_params(params)
        tags = [(tag.name, tag.entry_count) for tag in model.Tag.select()
          if tag.entry_count]
        tags.sort(key=lambda x: x[1])
        tags.reverse()
        params['tags'] = tags


class SearchForm(Form):
    """A simple search form with two different submit buttons."""

    template = """\
    <form xmlns:py="http://purl.org/kid/ns#"
        name="${name}"
        action="${action}"
        method="${method}"
        class="searchform"
        py:attrs="form_attrs"
    >
        <div py:for="field in hidden_fields"
            py:replace="field.display(value_for(field), **params_for(field))" />
        <div py:for="i, field in enumerate(fields)" class="searchfields">
          <span
            py:replace="field.display(value_for(field), **params_for(field))" />
          <span py:if="error_for(field)" class="fielderror"
            py:content="error_for(field)" />
          <div py:if="field.help_text" class="fieldhelp">
            <div py:content="field.help_text" />
          </div>
        </div>
        <div py:for="btn in submit"
            py:replace="btn.display(btn.label)" />
    </form>
    """
    javascript = [
      events,
      JSLink("cblog", "javascript/searchform.js")
    ]

class SearchFormFields(WidgetsList):
    q = TextField('q', label=_(u'Search post'),
        help_text=_(u'Enter search term (case-insensitive) [s]'),
        attrs=dict(maxlength=50, accesskey='s'))

class SearchFormSchema(validators.Schema):
    q = validators.UnicodeString(not_empty=True, max=50, strip=True)


# create instance of all site-wide widgets on import
archive_links = ArchiveLinks()

category_links = CategoryLinks()

fancyflash = FancyFlash()

gravatar = Gravatar(
  url='/gravatar',
  size=config.get('gravatars.size', 80),
  rating=config.get('gravatars.rating', 'R'),
  default=config.get('gravatars.default_image_url', None))

profile = Profile()

search_form = SearchForm(
    name='searchform',
    fields=SearchFormFields(),
    submit=[SubmitButton('title', label=_(u'Title')),
      SubmitButton('fulltext', label=_(u'Text'))],
    validator=SearchFormSchema())
