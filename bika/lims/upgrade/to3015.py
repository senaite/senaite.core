from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims.permissions import *
from Products.Archetypes.BaseContent import BaseContent
from bika.lims.upgrade import stub


def upgrade(tool):
    # Hack prevent out-of-date upgrading
    # Related: PR #1484
    # https://github.com/bikalabs/Bika-LIMS/pull/1484
    from bika.lims.upgrade import skip_pre315
    if skip_pre315(aq_parent(aq_inner(tool))):
        return True

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')

    stub('bika.lims.content.invoicelineitem', 'InvoiceLineItem',
        BaseContent)
    for inv in portal['invoices'].objectValues():
        inv.invoice_lineitems = []
        for invl in inv.objectValues():
            item = dict(
                ItemDate=invl.ItemDate,
                ItemDescription=invl.ItemDescription,
                ClientOrderNumber=invl.ClientOrderNumber,
                Subtotal=invl.Subtotal,
                VATAmount=invl.VATAmount,
                Total=invl.Total,
            )
            inv.invoice_lineitems.append(item)
    return True
