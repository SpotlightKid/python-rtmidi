<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import sitetemplate ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="sitetemplate">

<head py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'" py:attrs="item.items()">
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title py:replace="''">Your title goes here</title>
    <meta py:replace="item[:]"/>
<style type="text/css" media="screen">
@import "/static/css/style.css";
</style>
</head>

<body py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'" py:attrs="item.items()">

    <div py:if="tg_flash" class="flash" py:content="tg_flash"></div>

    <div id="header">&nbsp;</div>

    <div id="pageLogin">
      <div py:if="tg.config('identity.on',False) and not 'logging_in' in locals()" class="right">
        <span py:if="tg.identity.anonymous">
            <a href="/login">Login</a>
        </span>
        <span py:if="not tg.identity.anonymous">
            Welcome ${tg.identity.user.display_name}.
            <a href="/logout">Logout</a>
        </span>
      </div>
      <div class="left">
        <a href="${tg.url('/')}">Home</a>
        <a href="${tg.url('/bookmarks/')}">Bookmarks</a>
        <span py:if="'admin' in tg.identity.permissions" py:strip="">
          <a href="${tg.url('/users/')}">Users</a>
        </span>
      </div>
    </div>

    <div py:replace="[item.text]+item[:]"/>

	<!-- End of main_content -->
<div id="footer">
  <p>
    <a href="http://chrisarndt.de/projects/bookmarker/">Bookmarker homepage</a>
    <a href="http://turbogears.org/">Powered by TurboGears</a>
  </p>
</div>
</body>

</html>
