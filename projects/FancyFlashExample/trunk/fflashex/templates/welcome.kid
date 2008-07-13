<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Welcome to TurboFancyFlash</title>
</head>

<body>
  <h2>Wot do you mean, "TurboFancyFlash approaching"? Open fire!</h2>

  <p>Test the fancy flash messages:</p>

  <noscript>
  <p class="notice">Please turn JavaScript on to experience the full glory of
  FancyFlash!</p>
  </noscript>

  <ol>
    <li>Plain old
      <a href="${tg.url('/flash/flash')}" 
        title="Uses standard turbogears.flash() function."
        ><code>turbogears.flash()</code></a>, spiced up a bit
      <script type="text/javascript">
        document.write(' (click flash message to dismiss it)')
      </script>.
    </li>
    <li>Customers are requested to read the following
      <a title="Uses fancyflash.info() and 'timeout' parameter."
        href="${tg.url('/flash/info?timeout=5')}">information</a>
        carefully.</li>
    <li>Beware of <a title="Uses fancyflash.warning()."
        href="${tg.url('/flash/warning')}">this link</a>!</li>
    <li>What about HTML in messages?
      <a title="Uses fancyflash.error()."
      href="${tg.url('/flash/error')}">Try yourself</a></li>
    <li>But you can enable it, of course:
      <a title="Uses 'allow_html=True' parameter."
      href="${tg.url('/flash/showoff')}">show off</a></li>
    <li>And what about Unicode characters?
      <a title="Uses fancyflash.succcess()."
      href="${tg.url('/flash/success')}">Test it</a></li>
  </ol>

  <h3>Dynamic message boxes with JavaScript</h3>

  <p>You don't need to reload the page just to show a message. You can
  display messages with a simple JavaScript function call, for example
  in your callback function for <code>loadJSONDoc</code>. Enter a message
  in the text box below and then click on one of the following links to
  test it:</p>

  <p>Message:&nbsp;<input type="text" size="60" id="te_msg"
    value="Type test message here..."/></p>

  <ol>
    <li><a id="fancy_info" href="#">Information</a></li>
    <li><a id="fancy_warning" href="#">Warning</a></li>
    <li><a id="fancy_error" href="#">Error</a></li>
    <li><a id="fancy_success" href="#">Confirmation</a></li>
  </ol>

  <p>Thanks for trying TurboFancyFlash! Visit the
    <a href="http://chrisarndt.de/projects/fancyflash/"
    >TurboFancyFlash homepage</a> for more information and to look for new
    versions.</p>

</body>
</html>
