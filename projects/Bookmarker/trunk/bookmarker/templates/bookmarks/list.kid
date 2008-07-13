<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Bookmarker: ${title}</title>
</head>
<body>
<div id="main_content">
<h1 py:content="heading" />

<p><a href="${tg.url('/bookmarks/add')}">Add new bookmark</a></p>

<?python item = tg.ipeek(entries) ?>

<div py:if="item" class="bookmarks">

<dl py:for="bookmark in entries">
  <dt>
    <a href="${bookmark.url}" py:content="bookmark.title" />
  </dt>
  <dd>
    <p py:content="bookmark.description" />
    
    <ul class="taglist">
      <li py:for="tag in bookmark.tags">
        <a href="${tg.url('/bookmarks/tag/%s' % tag.name)}"
          >${tag.label}</a>
      </li>
    </ul>
    
    <p class="editlink"><a 
      href="${tg.url('/bookmarks/%i/edit' % bookmark.id)}">View/Edit
      details</a></p>
  </dd>
</dl>
</div>
<div py:if="not item" class="bookmarks">
No bookmarks found
</div>
</div>
</body>
</html>
