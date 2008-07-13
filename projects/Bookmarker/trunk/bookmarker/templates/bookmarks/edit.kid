<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>${title}</title>
</head>
<body>
<div id="main_content">
<h1 py.content="heading" />

<p><a href="${tg.url('/bookmarks/')}">back</a></p>

${form.display(data, submit_text=submit_text, action=action, method='POST')}
</div>
</body>
</html>
