<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:py="http://purl.org/kid/ns#">

  <id py:content="id">id</id>
  <title py:if="hasattr(self, 'title')" py:content="title">myfeed</title>
  <updated py:if="hasattr(self, 'updated')" py:content="updated">updated</updated>
  <author py:if="hasattr(self, 'author')">
    <name py:content="author['name']">name</name>
  </author>
  <link py:if="hasattr(self, 'href')" rel="self" href="${href}" />
  <icon py:if="hasattr(self, 'icon')" py:content="icon">icon</icon>
  <logo py:if="hasattr(self, 'logo')" py:content="logo">logo</logo>
  <rights py:if="hasattr(self, 'rights')" py:content="rights">rights</rights>
  <subtitle py:if="hasattr(self, 'subtitle')" py:content="subtitle">subtitle</subtitle>
  <category py:for="cat in categories" term="${cat}" label="${cat}" />

  <entry py:for="entry in entries">
    <title py:if="entry.has_key('title')" py:content="entry['title']">title</title>
    <id py:if="entry.has_key('id')" py:content="entry['id']">id</id>
    <updated py:if="entry.has_key('updated')" py:content="entry['updated']">updated</updated>
    <link py:if="entry.has_key('link')" rel="alternate" href="${entry['link']}" />
    <published py:if="entry.has_key('published')" py:content="entry['published']">published</published>
    <author py:if="entry.has_key('author')">
        <name py:content="author['name']">name</name>
    </author>
    <content py:if="entry.has_key('content')" py:content="entry['content']['value']" type="${entry['content']['type']}">content</content>
    <summary py:if="entry.has_key('summary')" py:content="entry['summary']">summary</summary>
    <rights py:if="entry.has_key('rights')" py:content="entry['rights']">rights</rights>
    <category py:for="cat in entry['categories']" term="${cat}" label="${cat}" />
  </entry>

</feed>
