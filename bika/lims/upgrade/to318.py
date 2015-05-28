from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.Archetypes.BaseContent import BaseContent
from bika.lims.upgrade import stub


def upgrade(tool):
    """Upgrade step required for Bika LIMS 3.1.8
    """
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    # Reread typeinfo to update/add the modified/added types
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    # Updated profile steps
    setup.runImportStepFromProfile('profile-bika.lims:default', 'jsregistry')

    # Migrations
    HEALTH245(portal)

    return True

def HEALTH245(portal):
    """ Set the '-' as default separator in all ids. Otherwise, new
        records will be created without '-', which has been used since
        now by default
    """
    for p in portal.bika_setup.getPrefixes():
        p['separator']='-' if not p['separator'] else p['separator']
