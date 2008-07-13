<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Welcome to TurboGears</title>
</head>
<body>
<div id="main_content">

  <h2>Welcome to the Bookmarker TurboGears demo!</h2>
  
  <div id="sidebar">
    <h2>Learn more</h2>
    Learn more about TurboGears and take part in its
    development
    <ul class="links">
      <li><a href="http://www.turbogears.org">Official website</a></li>
      <li><a href="http://docs.turbogears.org">Documentation</a></li>
      <li><a href="http://trac.turbogears.org/turbogears/">Trac
        (bugs/suggestions)</a></li>
      <li>
        <a href="http://groups.google.com/group/turbogears">Mailing list</a> 
      </li>
    </ul>
  </div>

  <div id="status_block">
    <p style="font-size: larger; text-align: center;">Try the
      <a href="${tg.url('/bookmarks/')}">Bookmarker demo</a> now
      (log in with username/password <code>test</code>)</p>
  </div>

  <div class="notice"> If you create something cool, please 
    <a href="http://groups.google.com/group/turbogears">let people know</a>, 
    and consider contributing something back to the 
    <a href="http://groups.google.com/group/turbogears">community</a>.
  </div>
</div>
</body>
</html>
