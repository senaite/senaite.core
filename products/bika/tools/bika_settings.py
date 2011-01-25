from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from Products.bika.tools import ToolFolder
from Products.bika.interfaces.tools import Ibika_settings
from five import grok

class bika_settings(ToolFolder):
    """ Container for bika settings """

    grok.implements(Ibika_settings)

    security = ClassSecurityInfo()
    id = 'bika_settings'
    title = 'Bika Settings'
    description = 'Configure password lifetime, auto log-off, VAT % and system prefixes.'
    meta_type = 'Bika Settings Tool'
    managed_portal_type = 'Laboratory'
    listing_schema = None
    default_template = 'tool_settings_view'

InitializeClass(bika_settings)
