from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore import permissions
from Products.bika.SamplePoint import schema as samplepoint_schema
from Products.bika.tools import ToolFolder
from Products.bika.utils import make_listing_from_schema
from Products.bika.interfaces.tools import Ibika_samplepoints
from five import grok

columns = ('title', 'SamplePointDescription')
samplepoint_listing = make_listing_from_schema(samplepoint_schema, columns)

class bika_samplepoints(ToolFolder):
    """ Container for sample points """

    grok.implements(Ibika_samplepoints)

    security = ClassSecurityInfo()
    id = 'bika_samplepoints'
    title = 'Sample Points'
    description = ''
    meta_type = 'Bika Sample Points Tool'
    managed_portal_type = 'SamplePoint'
    listing_schema = samplepoint_listing 

InitializeClass(bika_samplepoints)
