from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore import permissions
from bika.lims.ClientInvoicePreference import schema as invoicepref_schema
from bika.lims.tools import ToolFolder
from bika.lims.utils import make_listing_from_schema
from bika.lims.interfaces.tools import Ibika_invoice_prefs
from zope.interface import implements

columns = ('title',)
invoicepref_listing = make_listing_from_schema(invoicepref_schema, columns)

class bika_invoice_prefs(ToolFolder):
    """ Container for client invoice preferences """

    implements(Ibika_invoice_prefs)

    security = ClassSecurityInfo()
    id = 'bika_invoice_prefs'
    title = 'Invoice preferences'
    description = ''
    meta_type = 'Bika Invoice Preferences Tool'
    managed_portal_type = 'ClientInvoicePreference'
    listing_schema = invoicepref_listing

InitializeClass(bika_invoice_prefs)
