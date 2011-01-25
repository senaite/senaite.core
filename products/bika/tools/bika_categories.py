from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore import permissions
from Products.bika.AnalysisCategory import schema as category_schema
from Products.bika.tools import ToolFolder
from Products.bika.utils import make_listing_from_schema
from Products.bika.interfaces.tools import Ibika_categories
from five import grok

columns = ('title',)
category_listing = make_listing_from_schema(category_schema, columns)

class bika_categories(ToolFolder):
    """ Container for analysis categories"""

    grok.implements(Ibika_categories)

    security = ClassSecurityInfo()
    id = 'bika_categories'
    title = 'Analysis Categories'
    description = 'Setup the categories for the analysis services'
    meta_type = 'Bika categories Tool'
    managed_portal_type = 'AnalysisCategory'
    listing_schema = category_listing 

InitializeClass(bika_categories)
