# -*- coding: UTF-8 -*-

__all__ = ['article_form', 'ArticleForm']

from turbogears import validators, url
from turbogears.widgets import *

from cblog.widgets.base import *
from cblog.widgets import jslibs

article_css = [CSSLink("cblog", "css/articleform.css", media="screen")]
article_js = [
  jslibs.events,
  JSLink("cblog", "javascript/articleform.js"),
  JSLink("cblog", "javascript/forms.js")
]

class ArticleForm(Form):
    template = """\
    <div xmlns:py="http://purl.org/kid/ns#" id="articleform_wrapper">
      <div id="articlepreview" class="article"></div>

      <form
        name="${name}"
        action="${action}"
        method="${method}"
        class="fieldsetform"
        py:attrs="form_attrs">
        <div py:for="field in hidden_fields"
          py:replace="field.display(value_for(field), **params_for(field))"
        />
        <fieldset>
          <legend>Post new article</legend>

          <div py:for="i, field in enumerate(fields)"
            class="${i%2 and 'odd' or 'even'}${error_for(field) and ' fielderror' or ''}">
            <label class="fieldlabel" for="${field.field_id}" py:content="callable(field.label) and field.label() or field.label" />
            <span py:replace="field.display(value_for(field), **params_for(field))" />
            <span py:if="error_for(field)" class="fielderror" py:content="error_for(field)" />
            <div py:if="field.help_text" class="fieldhelp">
              <div py:content="field.help_text" />
            </div>
          </div>

        </fieldset>

        <fieldset>
          <legend>Add from your tags</legend>

          <div id="taglist">
            <p py:strip="True" py:for="tag, rank in tags">
              <a class="tag rank${rank}" href="#">${tag}</a>,
            </p>
            <div CLASS="fieldhelp">
              <div>Click on a tag to add it to the article.</div>
            </div>
          </div>
        </fieldset>

        <div class="buttonbox">
          <p py:replace="submit.display(submit_text)" />
        </div>
      </form>
    </div>
    """
    submit = SubmitButton(attrs=dict(id='submit_article'))
    javascript = article_js
    css = article_css


class ArticleFormFields(WidgetsList):
    id = HiddenField('id')
    title = TextField('title',
      label=_(u'Title'), attrs=dict(maxlength=255),
      help_text=_(u'The title of your blog article - no formatting. Required'))
    text = TextArea('text',
      label=HelplinkLabel(_(u'Text'), linklabel=_(u'Formatting help'),
        url=lambda:url('/static/rest.html')),
      attrs=dict(maxlength=50000),
      help_text=_(u'The text of your blog article in ReST format. Required'),
      rows=15)
    tags = TextField('tags',
      label=_(u'Tags'), attrs=dict(maxlength=1024),
      help_text=_(u"A comma-separated list of tags. e.g. 'Web Design' counts as one tag 'Web, Design' as two. Optional"))


class ArticleFormSchema(validators.Schema):
    id = validators.Int(default=None)
    title = validators.UnicodeString(not_empty=True, max=255, strip=True)
    text = validators.UnicodeString(not_empty=True, max=50000, strip=True)
    tags = validators.UnicodeString(max=1024, strip=True)

article_form = ArticleForm(
    name="articleform",
    fields=ArticleFormFields(),
    validator=ArticleFormSchema())
