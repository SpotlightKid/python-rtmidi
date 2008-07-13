BEGIN TRANSACTION;
INSERT INTO "tg_group" VALUES(1, 'admin', 'Administrators', '2006-08-19 11:30:39');
INSERT INTO "tg_group" VALUES(2, 'publisher', 'Blog publishers', '2006-08-21 01:19:00');
INSERT INTO "tg_group" VALUES(3, 'user', 'Standard users', '2006-08-21 01:20:00');

INSERT INTO "permission" VALUES(1, 'admin', 'Use the administration interface');
INSERT INTO "permission" VALUES(2, 'add_article', 'Post a blog article');
INSERT INTO "permission" VALUES(3, 'add_comment', 'Add a comment to a blog entry');

INSERT INTO "group_permission" VALUES(1, 1);
INSERT INTO "group_permission" VALUES(2, 2);
INSERT INTO "group_permission" VALUES(3, 3);

INSERT INTO "tg_user" VALUES(1, 'admin', 'root@localhost.localdomain', 'Administrator', '21232f297a57a5a743894a0e4a801fc3', '2006-08-19 11:26:45');

INSERT INTO "user_group" VALUES(1, 1);

INSERT INTO "tag" VALUES(1, 'General');

INSERT INTO "entry" VALUES(1, '2006-11-30 00:00:01', 1, 'Welcome to CBlog!', 'Since you can read this, you probably have already accomplished the installation and setup of your CBlog application.

**Congratulations!**

What to do next:
----------------

  1. Log in with username and password ``admin`` and click on *Administration* (at the bottom of the sidebar to the left).
  2. Create a new user and add him to the *Blog publishers* group.
  3. Close the administration window, log out and then log in again as the new user.
  4. Click on *Post new article* and start adding articles to your blog.

**Share and enjoy!**', '<div class="document">
<p>Since you can read this, you probably have already accomplished the installation and setup of your CBlog application.</p>
<p><strong>Congratulations!</strong></p>
<div class="section">
<h1><a id="what-to-do-next" name="what-to-do-next">What to do next:</a></h1>
<blockquote>
<ol class="arabic simple">
<li>Log in with username and password <tt class="docutils literal"><span class="pre">admin</span></tt> and click on <em>Administration</em> (at the bottom of the sidebar to the left).</li>
<li>Create a new user and add him to the <em>Blog publishers</em> group.</li>
<li>Close the administration window, log out and then log in again as the new user.</li>
<li>Click on <em>Post new article</em> and start adding articles to your blog.</li>
</ol>
</blockquote>
<p><strong>Share and enjoy!</strong></p>
</div>
</div>
');

INSERT INTO "entry_tag" VALUES(1, 1);

COMMIT;
