BEGIN TRANSACTION;
CREATE TABLE bookmark (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    url VARCHAR(255) NOT NULL,
    description TEXT,
    created TIMESTAMP,
    owner_id INT NOT NULL CONSTRAINT owner_id_exists REFERENCES tg_user(id)
);
INSERT INTO "bookmark" VALUES(1, 'Official Python homepage', 'http://python.org/', 'The first stop for any Python user, novice or expert. Has excellent documentation, links to community sites, mailings lists and much more...', '2006-12-05 00:52:00', 1);
INSERT INTO "bookmark" VALUES(2, 'TurboGears: Front-to-Back Web Development', 'http://turbogears.org/', 'Create a database-driven, ready-to-extend application in minutes. All with designer friendly templates, easy AJAX on the browser side and on the server side, not a single SQL query in sight with code that is as natural as writing a function.', '2006-12-05 04:58:28', 1);
INSERT INTO "bookmark" VALUES(3, 'CherryPy', 'http://cherrypy.org/', 'CherryPy is a pythonic, object-oriented HTTP framework. It allows developers to build web applications in much the same way they would build any other object-oriented Python program. This usually results in smaller source code developed in less time.goo', '2006-12-05 05:00:52', 1);
INSERT INTO "bookmark" VALUES(4, 'pyCologne - Python User Group Köln', 'http://wiki.python.de/pyCologne', 'pyCologne is a young Python Python User Group (PUG), created by Python enthusiasts from Cologne, Germany and the surrounding area. Our page on the German Python Wiki gives the most important facts about our group.', '2006-12-14 22:43:00', 1);
INSERT INTO "bookmark" VALUES(5, 'SQLObject homepage', 'http://sqlobject.org/', 'SQLObject is an object relational mapper for Python.', '2006-12-23 04:28:49', 2);
INSERT INTO "bookmark" VALUES(6, 'Das Deutsche Python Wiki', 'http://wiki.python.de/', 'Deutsches Wiki für Python', '2006-12-23 04:38:28', 2);
CREATE TABLE bookmark_tag (
bookmark_id INT NOT NULL,
tag_id INT NOT NULL
);
INSERT INTO "bookmark_tag" VALUES(1, 1);
INSERT INTO "bookmark_tag" VALUES(1, 4);
INSERT INTO "bookmark_tag" VALUES(2, 1);
INSERT INTO "bookmark_tag" VALUES(2, 8);
INSERT INTO "bookmark_tag" VALUES(2, 9);
INSERT INTO "bookmark_tag" VALUES(3, 1);
INSERT INTO "bookmark_tag" VALUES(3, 8);
INSERT INTO "bookmark_tag" VALUES(3, 10);
INSERT INTO "bookmark_tag" VALUES(5, 11);
INSERT INTO "bookmark_tag" VALUES(5, 12);
INSERT INTO "bookmark_tag" VALUES(5, 13);
INSERT INTO "bookmark_tag" VALUES(5, 14);
INSERT INTO "bookmark_tag" VALUES(6, 11);
INSERT INTO "bookmark_tag" VALUES(6, 15);
INSERT INTO "bookmark_tag" VALUES(4, 17);
INSERT INTO "bookmark_tag" VALUES(4, 4);
INSERT INTO "bookmark_tag" VALUES(4, 5);
INSERT INTO "bookmark_tag" VALUES(4, 1);
CREATE TABLE tg_group (
    id INTEGER PRIMARY KEY,
    group_name VARCHAR(16) NOT NULL UNIQUE,
    display_name VARCHAR(255),
    created TIMESTAMP
);
INSERT INTO "tg_group" VALUES(1, 'admin', 'Administrators', '2007-04-09 22:09:00');
CREATE TABLE user_group (
group_id INT NOT NULL,
user_id INT NOT NULL
);
INSERT INTO "user_group" VALUES(1, 1);
CREATE TABLE group_permission (
group_id INT NOT NULL,
permission_id INT NOT NULL
);
INSERT INTO "group_permission" VALUES(1, 1);
CREATE TABLE permission (
    id INTEGER PRIMARY KEY,
    permission_name VARCHAR(16) NOT NULL UNIQUE,
    description VARCHAR(255)
);
INSERT INTO "permission" VALUES(1, 'admin', 'Administrative tasks');
CREATE TABLE tag (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    label VARCHAR(100) NOT NULL,
    owner_id INT NOT NULL CONSTRAINT owner_id_exists REFERENCES tg_user(id) ,
    created TIMESTAMP
);
INSERT INTO "tag" VALUES(1, 'python', 'Python', 1, '2006-12-05 00:51:00');
INSERT INTO "tag" VALUES(2, 'web design', 'Web design', 1, '2006-12-05 00:51:00');
INSERT INTO "tag" VALUES(3, 'science fiction', 'Science fiction', 1, '2006-12-05 00:52:00');
INSERT INTO "tag" VALUES(4, 'homepage', 'Homepage', 1, '2006-12-14 22:16:59');
INSERT INTO "tag" VALUES(5, 'pug', 'PUG', 1, '2006-12-14 22:43:12');
INSERT INTO "tag" VALUES(7, 'turbogears', 'TurboGears', 1, '2006-12-14 22:45:18');
INSERT INTO "tag" VALUES(8, 'web development', 'Web development', 1, '2006-12-14 22:45:18');
INSERT INTO "tag" VALUES(9, 'framework', 'Framework', 1, '2006-12-14 22:45:18');
INSERT INTO "tag" VALUES(10, 'application server', 'Application Server', 1, '2006-12-15 00:22:26');
INSERT INTO "tag" VALUES(11, 'python', 'Python', 2, '2006-12-23 04:28:49');
INSERT INTO "tag" VALUES(12, 'orm', 'ORM', 2, '2006-12-23 04:28:49');
INSERT INTO "tag" VALUES(13, 'sql', 'SQL', 2, '2006-12-23 04:28:49');
INSERT INTO "tag" VALUES(14, 'python module', 'Python module', 2, '2006-12-23 04:28:49');
INSERT INTO "tag" VALUES(15, 'german', 'German', 2, '2006-12-23 04:38:28');
INSERT INTO "tag" VALUES(17, 'cologne', 'Cologne', 1, '2007-04-09 20:49:23');
INSERT INTO "tag" VALUES(18, 'köln', 'Köln', 1, '2007-04-09 23:26:11');
CREATE TABLE tg_user (
    id INTEGER PRIMARY KEY,
    user_name VARCHAR(16) NOT NULL UNIQUE,
    email_address VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255),
    password VARCHAR(40),
    created TIMESTAMP
);
INSERT INTO "tg_user" VALUES(1, 'test', 'test@localhost.localdomain', 'Test user', 'test', '2006-12-05 00:50:00');
INSERT INTO "tg_user" VALUES(2, 'joe', 'joe@doe.com', 'Joe Doe', 'jane', '2006-12-23 04:24:00');
CREATE TABLE visit (
    id INTEGER PRIMARY KEY,
    visit_key VARCHAR(40) NOT NULL UNIQUE,
    created TIMESTAMP,
    expiry TIMESTAMP
);
CREATE TABLE visit_identity (
    id INTEGER PRIMARY KEY,
    visit_key VARCHAR(40) NOT NULL UNIQUE,
    user_id INT
);
CREATE TABLE tg_visit_identity (
    id INTEGER PRIMARY KEY,
    visit_key VARCHAR(40) NOT NULL UNIQUE,
    user_id INT
);
CREATE TABLE tg_visit (
    id INTEGER PRIMARY KEY,
    visit_key VARCHAR(40) NOT NULL UNIQUE,
    created TIMESTAMP,
    expiry TIMESTAMP
);
CREATE TABLE tg_permission (
    id INTEGER PRIMARY KEY,
    child_name VARCHAR(255),
    permission_name VARCHAR(16) NOT NULL UNIQUE,
    description VARCHAR(255)
);
COMMIT;
