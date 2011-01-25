from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore import permissions
from Products.bika.Instrument import schema as instrument_schema
from Products.bika.tools import ToolFolder
from Products.bika.utils import make_listing_from_schema
from Products.bika.interfaces.tools import Ibika_instruments
from five import grok

columns = ('title', 'Type', 'Brand', 'Model', 'ExpiryDate')
instrument_listing = make_listing_from_schema(instrument_schema, columns)

class bika_instruments(ToolFolder):
    """ Container for lab instruments """

    grok.implements(Ibika_instruments)

    security = ClassSecurityInfo()
    id = 'bika_instruments'
    title = 'Lab instruments'
    description = 'Setup the instruments used in the lab.'
    meta_type = 'Bika Instruments Tool'
    managed_portal_type = 'Instrument'
    listing_schema = instrument_listing 

InitializeClass(bika_instruments)

