from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.Archetypes.BaseContent import BaseContent
from Products.CMFCore.utils import getToolByName
from bika.lims.upgrade import stub


def LIMS1519(portal):
    """Migrate Archetypes SupplyOrderItem into a list of dictionaries.
    """
    stub('bika.lims.content.supplyorderitem', 'SupplyOrderItem',
         BaseContent)
    for order in portal['supplyorders'].objectValues():
        order.supplyorder_lineitems = []
        for soli in order.objectValues():
            item = dict(
                Product=soli.Product,
                Quantity=soli.Quantity,
                Price=soli.Price,
                VAT=soli.VAT,
            )
            order.supplyorder_lineitems.append(item)

def LIMS1546(portal):
    """Set catalogs for SRTemplate
    """
    at = getToolByName(portal, 'archetype_tool')
    at.setCatalogsByType('SRTemplate', ['bika_setup_catalog', 'portal_catalog'])
    for obj in portal.bika_setup.bika_srtemplates.objectValues():
        obj.unmarkCreationFlag()
        obj.reindexObject()


def upgrade(tool):
    """Upgrade step required for Bika LIMS 3.1.7
    """
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    # Updated profile steps

    setup.runImportStepFromProfile('profile-bika.lims:default', 'cssregistry')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'jsregistry')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'propertiestool')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow-csv')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'plone.app.registry')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'controlpanel')

    # Migrations

    LIMS1519(portal)
    LIMS1546(portal)

    return True
