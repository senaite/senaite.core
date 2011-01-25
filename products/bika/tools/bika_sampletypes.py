from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore import permissions
from Products.bika.SampleType import schema as sampletype_schema
from Products.bika.tools import ToolFolder
from Products.bika.utils import make_listing_from_schema
from Products.bika.interfaces.tools import Ibika_sampletypes
from five import grok

columns = ('title', 'SampleTypeDescription')
sampletype_listing = make_listing_from_schema(sampletype_schema, columns)

class bika_sampletypes(ToolFolder):
    """ Container for sample types """

    grok.implements(Ibika_sampletypes)

    security = ClassSecurityInfo()
    id = 'bika_sampletypes'
    title = 'Sample Types'
    description = ''
    meta_type = 'Bika Sample Types Tool'
    managed_portal_type = 'SampleType'
    listing_schema = sampletype_listing 

InitializeClass(bika_sampletypes)
