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
    <div id="header">&nbsp;</div>

  <div id="main_content">
    <div py:replace="tg_fancyflashwidget(tg_flash)">Status message
      appears here</div>

    <div py:replace="[item.text]+item[:]"/>

    <pre class="debugout" py:if="getattr(tg, 'pformat', None)"
      py:content="tg.pformat(self.__dict__, indent=2, depth=5)"
      >Template variables debugging output</pre>
  </div>

  <div id="footer">
    <a href="http://www.turbogears.org/"><img
      src="/static/images/under_the_hood_blue.png" border="0"/></a>
    <p>TurboGears is a open source front-to-back web development
    framework written in Python</p>
    <p>Copyright &copy; 2006-2008 Kevin Dangoor</p>
  </div>
</body>

</html>
