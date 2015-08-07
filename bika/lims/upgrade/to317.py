from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.Archetypes.BaseContent import BaseContent
from bika.lims.upgrade import stub
from bika.lims import logger


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


def upgrade(tool):
    """Upgrade step required for Bika LIMS 3.1.7
    """
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    qi = portal.portal_quickinstaller
    ufrom = qi.upgradeInfo('bika.lims')['installedVersion']
    logger.info("Upgrading Bika LIMS: %s -> %s" % (ufrom, '317'))

    # Updated profile steps

    setup.runImportStepFromProfile('profile-bika.lims:default', 'jsregistry')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow-csv')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'plone.app.registry')

    # Migrations

    LIMS1519(portal)

    return True
