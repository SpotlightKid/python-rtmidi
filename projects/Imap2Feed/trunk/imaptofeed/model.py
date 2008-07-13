from turbogears.database import PackageHub
from sqlobject import *

hub = PackageHub('imaptofeed')
__connection__ = hub

# class YourDataClass(SQLObject):
#     pass
 
