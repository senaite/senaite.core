from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore import permissions
from Products.bika.CalculationType import schema as calctype_schema
from Products.bika.tools import ToolFolder
from Products.bika.utils import make_listing_from_schema
from Products.bika.interfaces.tools import Ibika_calctypes
from five import grok

columns = ('title', 'CalculationTypeDescription')
calctype_listing = make_listing_from_schema(calctype_schema, columns)

class bika_calctypes(ToolFolder):
    """ Container for departments"""

    grok.implements(Ibika_calctypes)

    security = ClassSecurityInfo()
    id = 'bika_calctypes'
    title = 'Calculation types'
    description = 'Setup the calculation types used for analyses'
    meta_type = 'Bika Calculation Types Tool'
    managed_portal_type = 'CalculationType'
    listing_schema = calctype_listing 

InitializeClass(bika_calctypes)
