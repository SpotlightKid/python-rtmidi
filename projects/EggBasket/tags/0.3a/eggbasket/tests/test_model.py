"""Unit test cases for testing you application's model classes.

If your project uses a database, you should set up database tests similar to
what you see below.

Be sure to set the ``db_uri`` in the ``test.cfg`` configuration file in the
top-level directory of your project to an appropriate uri for your testing
database. SQLite is a good choice for testing, because you can use an in-memory
database which is very fast and the data in it has to be boot-strapped from
scratch every time, so the tests are independant of any pre-existing data.

You can also set the ``db_uri``directly in this test file but then be sure
to do this before you import your model, e.g.::

    from turbogears import testutil, database
    database.set_db_uri("sqlite:///:memory:")
    from eggbasket.model import YourModelClass, User, ...
"""

from turbogears import testutil, database

# from eggbasket.model import YourModelClass, User

# class TestUser(testutil.DBTest):
#     def get_model(self):
#         return User
#     def test_creation(self):
#         """Object creation should set the name."""
#         obj = User(user_name = "creosote",
#                 email_address = "spam@python.not",
#                 display_name = "Mr Creosote",
#                 password = "Wafer-thin Mint")
#         assert obj.display_name == "Mr Creosote"

