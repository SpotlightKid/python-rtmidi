# -*- coding: UTF-8 -*-

__all__ = ['comment_form', 'CommentForm']

from turbogears import validators, url
from turbogears.widgets import *

import cElementTree as ET

from cblog.widgets.validators import SpamFilter
from cblog.widgets.base import *
from cblog.widgets import jslibs

comment_css = [CSSLink("cblog", "css/commentform.css", media="screen")]
comment_js = [
  jslibs.events,
  JSLink("cblog", "javascript/forms.js"),
  JSLink("cblog", "javascript/commentform.js"),
  JSSource(
    "document.write('<style>#commentform_wrapper {display: none;}</style>');",
    js_location.head
  )
]

class CommentForm(ListForm):
    template = """\
    <div xmlns:py="http://purl.org/kid/ns#" id="commentform_wrapper">
      <div id="commentpreview" class="comment"></div>
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
          <legend>Add new comment</legend>

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

        <div class="buttonbox">
          <p py:replace="submit.display(submit_text)" />
        </div>
      </form>
    </div>
    """
    submit = SubmitButton(attrs=dict(
      id='submit_comment',
      accesskey='s',
      title='Save comment [s]'
    ))
    javascript = comment_js
    css = comment_css


class CommentFormFields(WidgetsList):
    id = HiddenField('id')
    name = TextField('name',
      label=_(u'Name'), attrs=dict(maxlength=50),
      help_text=_(u'Your name - will be displayed with your comment. Required'))
    email = TextField('email',
      label=_(u'Email'), attrs=dict(maxlength=255),
      help_text=_(u'Your email address - will not be displayed. Required'))
    homepage = TextField('homepage',
      label=_(u'Website'), attrs=dict(maxlength=255),
      help_text=_(u'Your homepage URL - your name will link to this. Optional'))
    comment = TextArea('comment',
      label=HelplinkLabel(_(u'Comment'), linklabel=_(u'Formatting help'),
        url=lambda:url('/static/textile.html')),
      help_text=_(u'Your comment - textile syntax, 1000 chars max. Required'),
      rows=7)


class CommentFormSchema(validators.Schema):
    id = validators.Int(not_empty=True)
    name = validators.UnicodeString(not_empty=True, max=50, strip=True)
    email = validators.Email(not_empty=True, max=255, strip=True)
    homepage = validators.All(
      validators.UnicodeString(max=255, strip=True),
      validators.URL(add_http=True))
    comment = validators.UnicodeString(not_empty=True, max=1000)
    chained_validators = [SpamFilter()]

comment_form = CommentForm(
    name="commentform",
    fields=CommentFormFields(),
    validator=CommentFormSchema())
