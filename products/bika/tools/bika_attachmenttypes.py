from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore import permissions
from Products.bika.AttachmentType import schema as attachmenttype_schema
from Products.bika.tools import ToolFolder
from Products.bika.utils import make_listing_from_schema
from Products.bika.interfaces.tools import Ibika_attachmenttypes
from five import grok

columns = ('title', 'AttachmentTypeDescription')
attachmenttype_listing = make_listing_from_schema(attachmenttype_schema, columns)

class bika_attachmenttypes(ToolFolder):
    """ Container for Attachment Types """

    grok.implements(Ibika_attachmenttypes)

    security = ClassSecurityInfo()
    id = 'bika_attachmenttypes'
    title = 'Attachment types'
    description = 'Setup the attachment types'
    meta_type = 'Bika Attachment Types Tool'
    managed_portal_type = 'AttachmentType'
    listing_schema = attachmenttype_listing 

InitializeClass(bika_attachmenttypes)
