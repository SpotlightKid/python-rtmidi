# -*- coding: UTF-8 -*-

import logging
from datetime import datetime

import cherrypy

import turbogears
from turbogears import controllers, expose, validate, validators, redirect
from turbogears import error_handler, identity, url, config
from turbogears.toolbox.catwalk import CatWalk
from turbogears.view import variable_providers

from sqlobject import SQLObjectNotFound
from sqlobject.sqlbuilder import *

from dateutil.relativedelta import *

from cblog import model
from cblog.widgets import *
from cblog.fflash import *
from cblog.widgets.gravatar import GravatarController
from cblog.controllers.feed import *
from turbogears.util import Bunch

log = logging.getLogger('cblog.controllers')

# set timeout for status messages
set_default_message_timeout(5)

# register site-wide widgets to be included on every page
register_sitewidgets(sitewidgets, 'cblog.widgets')

def request_provider(state=None):
    """Provide request information to validation schemas."""

    if state is None:
        return Bunch(request=cherrypy.request)
    state.request = cherrypy.request
    return state

class Root(controllers.RootController):
    # allow users with permission 'admin' to acces the admin interface (CatWalk)
    # through 'http://myserver/admin'
    admin = CatWalk(model)
    admin = identity.SecureObject(admin, identity.has_permission('admin'))

    feed = CBlogFeedController('/feed')
    gravatar = GravatarController()

    def __init__(self, *args, **kw):
        super(Root, self).__init__(*args, **kw)
        variable_providers.append(self.add_viewutils)
        variable_providers.append(self.add_feeds)

    @expose(template='cheetah:cblog.templates.blog')
    def index(self):
        """Show the front page with the latest blog entries.

        The number of blog entries shown is configurable through
        the config file option 'cblog.frontpage.max_entries'.

        Articles are shown as teasers, i.e. the title and excerpts of the
        full text, sorted by date, most recent first.
        """

        max = config.get('cblog.frontpage.max_entries', 5)
        entries = model.Entry.select()
        return dict(entries=entries[:max])

    @expose(template='cheetah:cblog.templates.view')
    @validate(validators=dict(id=validators.Int()))
    def article(self, id, tg_errors=None):
        """Show a full article page with comments.

        Also show the comment submission form and error messages.
        """

        if tg_errors:
            if 'id' in tg_errors:
                error(_(u'Invalid article ID.'))
                redirect(url('/'))
            else:
                error(_(u'A problem occured saving your comment. '
                  u'Please correct your input.'))
        try:
            entry = model.Entry.get(id)
        except SQLObjectNotFound:
            error(_(u'No article with ID %i found.') % id)
            redirect(url('/'))
        else:
            comments = model.Comment.selectBy(entry=entry)
        return dict(entry=entry, comments=comments,
          comment_form=comment_form)
          #comment_form=None)

    @expose(template='cheetah:cblog.templates.blog')
    @validate(validators=dict(tagname=validators.UnicodeString(not_empty=True,
      max=100, strip=True)))
    def tag(self, tagname, tg_errors=None):
        """Show all articles categorized with given tag.

        The tag name is given by the 'tag' request variable and may
        contain spaces and unicode (utf-8) characters.

        Display format is the same as for the front page.
        """

        if tg_errors:
            error(_(u'Invalid tag name.'))
            redirect(url('/'))
        try:
            tag = model.Tag.byLabel(tagname)
        except SQLObjectNotFound:
            error(_(u"Tag '%s' not found.") % tagname)
            redirect(url('/'))
        return dict(entries=tag.entries, tag=tag)

    @expose(template='cheetah:cblog.templates.blog')
    def archive(self, date=None):
        """Show list of blog entries for given month.

        The month must be specified in the form yyyy-mm as a single
        request variable, e.g.

            http://myserver/archive/2006-10

        Display format is the same as for the front page.
        """

        # date will either be the first of given month/year or None
        if date is None:
            # no date given, show archive overview page
            return dict(tg_template='cheetah:cblog.templates.archive',
              numentries=model.Entry.select().count(),
              numcomments=model.Comment.select().count(),
              # FIXME: only count tags, which are really used
              numtags=model.Tag.select().count())
        else:
            try:
                year, month = (int(x) for x in date.split('-', 1))
                start_date = datetime(year, month, 1)
            except (IndexError, ValueError):
                error(_(u'The date must be specified as YYYY-MM'))
                redirect(url('/'))
            # set end date to first of next month
            end_date = start_date + relativedelta(months=+1)
            entries = model.Entry.select(
              AND(
                model.Entry.q.created >= start_date,
                model.Entry.q.created < end_date
              )
            )
            return dict(entries=entries)

    @expose(template='cheetah:cblog.templates.featured')
    def featured(self):
        """Show a list of 'featured' articles, i.e. articles with a review.'

        Articles are shown with the title and the review text and author,
        sorted by date, most recent first.
        """

        reviews = model.Review.select(model.Review.q.active == True,
          orderBy=model.Review.q.created).reversed()
        return dict(reviews=reviews)

    @expose(template='cheetah:cblog.templates.blog')
    @validate(form=search_form)
    def search(self, q, tg_errors=None, **kw):
        """Search the database for blog articles by title or fulltext.

        The query term is set by the request variable 'q' and is tokenised
        by the 'parse_search_query' method.

        If the request variable 'title' is true, only article titles are
        searched. Full text search is implemented by the method
        'search_entries_fulltext'.

        Display format is the same as for the front page.
        """

        if tg_errors:
            error(str(tg_errors['q']))
        tokens = self.parse_search_query(q)
        if kw.get('title'):
            E = model.Entry.q
            hits = set()
            for token in tokens:
                hits.update(
                  list(model.Entry.select(
                    E.title.contains(token))
                  )
                )
            entries = list(hits)
        else:
            entries = self.search_entries_fulltext(tokens)
        entries.sort(key=lambda x: x.created)
        entries.reverse()
        return dict(entries=entries)

    @expose(template='cheetah:cblog.templates.edit')
    @validate(validators=dict(id=validators.Int(default=None)))
    def edit_article(self, id=None, tg_errors=None):
        if tg_errors:
            if 'id' in tg_errors:
                error(_(u'Invalid article ID.'))
                redirect(url('/'))
            else:
                error(_(u'There was a problem with your submission. '
                  u'Please correct your input.'))
        if id:
            try:
                entry = model.Entry.get(id)
            except SQLObjectNotFound:
                error(_(u'No article with ID %i found.') % id)
                redirect(url('/'))
            else:
                if entry.author.user_name != identity.current.user_name:
                    raise identity.IdentityFailure(
                      _(u'Must be owner of article'))
                entry = dict(
                  id = entry.id,
                  title = entry.title,
                  text = entry.text,
                  tags = ", ".join(tag.name for tag in entry.tags)
                )
        else:
            entry = {}
        tags = [(tag.name, tag.entry_count) for tag in
          model.Tag.select(orderBy='name')]
        # build a table of tag usage counts
        counts = sorted(list(set([x[1] for x in tags])))
        # get position (rank) of each tag in the usage table
        # FIXME: usage count rank is currently clipped at 10
        tags = [(x[0], min(9, counts.index(x[1]))) for x in tags]
        return dict(form=article_form, entry=entry, tags=tags)

    @expose()
    @identity.require(identity.has_permission('add_article'))
    @validate(form=article_form)
    @error_handler(edit_article)
    def add_article(self, title, text, tags='', id=None, tg_errors=None):
        model.hub.begin()
        data = dict(
          title=title,
          text=text
        )
        if id is None:
            entry = model.Entry(
              author = model.User.by_user_name(identity.current.user_name),
              **data
            )
        else:
            try:
                entry = model.Entry.get(id)
            except SQLObjectNotFound:
                error(_(u'No article with ID %i found.') % id)
                redirect(url('/edit_article'))
            else:
                entry.set(**data)
        # update tags
        taglist = [tag.strip() for tag in tags.split(',')]
        entry.update_tags(taglist)

        model.hub.commit()
        success(_(u'Article has been saved.'))
        redirect(url('/article/%i' % entry.id))

    @expose()
    @identity.require(identity.has_permission('add_comment'))
    @validate(form=comment_form, state_factory=request_provider)
    @error_handler(article)
    def add_comment(self, id, name, email, comment, homepage=None):
        """Handle comment submissions.

        Comments are validated by the CommentForm widget, which also does
        spam detection through configurable filter plug-ins. See the
        'cblog.widgets.validators' module for more information.

        Comments are saved along with the IP address from which the comment
        was submitted, to allow later identification and spam protection
        by IP throttling.
        """

        try:
            entry = model.Entry.get(id)
        except SQLObjectNotFound:
            error(_(u'No article with id %i found.') % id)
            redirect(url('/'))
        model.hub.begin()
        comment = model.Comment(
            author = name,
            email = email,
            homepage = homepage,
            ipAddress = cherrypy.request.remote_addr or None,
            text = comment,
            entry = entry
        )
        model.hub.commit()
        success(_(u'Your comment has been saved.'))
        redirect(url('/article/%s' % id))

    @expose('json')
    @validate(validators=dict(text=validators.UnicodeString(not_empty=True,
      max=50000, strip=True)))
    def preview(self, text, format='textile', tg_errors=None, **kw):
        """Return formatted comment wrapped in a JSON container."""

        res = dict()
        if tg_errors:
            res['error'] = unicode(tg_errors.get('text',
              _(u'Error processing submitted data.')))
        else:
            try:
                # look for formatting function in 'model' module
                formatter = getattr(model, '%s2html' % format)
                res['preview'] = formatter(text)
            except Exception, exc:
                res['error'] = _('Error: Could not format text: %s') % exc
        return res

    @expose(template='cheetah:cblog.templates.login')
    def login(self, forward_url=None, previous_url=None, *args, **kw):

        if not identity.current.anonymous \
            and identity.was_login_attempted() \
            and not identity.get_identity_errors():
            raise redirect(forward_url)

        forward_url=None
        previous_url= cherrypy.request.path

        if identity.was_login_attempted():
            msg = _(u'The credentials you supplied were not correct or '
                   u'did not grant access to this resource.')
        elif identity.get_identity_errors():
            msg = _(u'You must provide your credentials before accessing '
                   'this resource.')
        else:
            msg = _(u'Please log in.')
            forward_url = cherrypy.request.headers.get('Referer', '/')
        cherrypy.response.status = 403
        return dict(message=msg, previous_url=previous_url, logging_in=True,
                    original_parameters=cherrypy.request.params,
                    forward_url=forward_url)

    @expose()
    def logout(self):
        identity.current.logout()
        raise redirect('/')

    def parse_search_query(self, query):
        """Split a search query string into search term tokes."""

        tokens = query.split()
        return [x.lower().replace('*', '%') for x in tokens]

    def search_entries_fulltext(self, tokens):
        """Search for tokens through all posts, comments and authors."""

        E = model.Entry.q
        C = model.Comment.q
        hits = set()
        for token in tokens:
            # search through post titles and text
            hits.update(
              list(model.Entry.select(
                OR(E.title.contains(token),
                  E.text.contains(token))
              ))
            )
            # search through comments and comment authors' names
            comments = list(model.Comment.select(
              OR(C.author.contains(token),
                C.text.contains(token))
            ))
            hits.update([x.entry for x in comments])
            # and through poster names
            # !KLUDGE!
            hits.update(list(model.Entry.select(
              "entry.author_id = tg_user.id AND "
              "tg_user.display_name LIKE %s" % \
                model.Entry.sqlrepr('%' + token + '%'),
              clauseTables=['tg_user'], orderBy="entry.created")
            ))
        return list(hits)

    def add_viewutils(self, d):
        """Add custom formatting functions to the 'tg' template namespace.

        See module utils.formatting for which functions are added.
        """

        m = __import__('cblog.utils.formatting', {}, {}, ['*'])
        for c in getattr(m, '__all__', []):
            d[c] = getattr(m, c)
        d['blogtitle'] = config.get('cblog.title', 'Unnamed blog')
        d['blogdesc'] = config.get('cblog.description', '')
        d['title'] = config.get('cblog.title', 'Unnamed blog')

    def add_feeds(self, d):
        """Add feed links to the 'tg' template namespace.

        BUG: adding feed links for /tag/<tag> pages does not work,
        because we don't have access the dicctionary returned by the
        controllers to find out the requested tag.
        Possible solution: turn feed links in to site-wide widgets.
        """

        feeds = dict(
          summary= self.feed.get_feed_info('atom1_0', format='summary'),
          full= self.feed.get_feed_info('atom1_0', format='full')
        )
        tag = d.get('tag')
        if tag:
            feeds[tag.name] = {}
            feeds[tag.name]['summary'] = \
              self.feed.get_feed_info('atom1_0', format='summary',
                tag=tag.name)
            feeds[tag.name]['full'] = \
              self.feed.get_feed_info('atom1_0', format='full',
                tag=tag.name)
        d['feeds'] = feeds
