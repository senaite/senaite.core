from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore import permissions
from Products.bika.Department import schema as department_schema
from Products.bika.interfaces.tools import Ibika_departments
from Products.bika.tools import ToolFolder
from Products.bika.utils import make_listing_from_schema
from five import grok

columns = ('title', 'ManagerName')
department_listing = make_listing_from_schema(department_schema, columns)

class bika_departments(ToolFolder):
    """ Container for departments"""

    grok.implements(Ibika_departments)

    security = ClassSecurityInfo()
    id = 'bika_departments'
    title = 'Lab departments'
    description = 'Setup the departments in the laboratory.'
    meta_type = 'Bika Departments Tool'
    managed_portal_type = 'Department'
    listing_schema = department_listing

InitializeClass(bika_departments)
