from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore import permissions
from Products.bika.LabContact import schema as labcontact_schema
from Products.bika.tools import ToolFolder
from Products.bika.utils import make_listing_from_schema
from Products.bika.interfaces.tools import Ibika_labcontacts
from five import grok

columns = ('title', 'BusinessPhone', 'MobilePhone', 'EmailAddress')
labcontact_listing = make_listing_from_schema(labcontact_schema, columns)

class bika_labcontacts(ToolFolder):
    """ Container for Lab Contacts """

    grok.implements(Ibika_labcontacts)

    security = ClassSecurityInfo()
    id = 'bika_labcontacts'
    title = 'Lab contacts'
    description = 'Setup the laboratory contacts.'
    meta_type = 'Bika Lab Contacts Tool'
    managed_portal_type = 'LabContact'
    listing_schema = labcontact_listing 

InitializeClass(bika_labcontacts)
