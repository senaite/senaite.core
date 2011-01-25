from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore import permissions
from Products.bika.WorksheetTemplate import schema as worksheettemplate_schema
from Products.bika.tools import ToolFolder
from Products.bika.utils import make_listing_from_schema
from Products.bika.interfaces.tools import Ibika_worksheettemplates
from five import grok

columns = ('title', 'WorksheetTemplateDescription')
worksheettemplate_listing = make_listing_from_schema(worksheettemplate_schema, columns)

class bika_worksheettemplates(ToolFolder):
    """ Container for worksheet templates """

    grok.implements(Ibika_worksheettemplates)

    security = ClassSecurityInfo()
    id = 'bika_worksheettemplates'
    title = 'Worksheet Templates'
    description = ''
    meta_type = 'Bika Worksheet Templates Tool'
    managed_portal_type = 'WorksheetTemplate'
    listing_schema = worksheettemplate_listing 

InitializeClass(bika_worksheettemplates)
