from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims.permissions import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest


def upgrade(tool):
    # Hack prevent out-of-date upgrading
    # Related: PR #1484
    # https://github.com/bikalabs/Bika-LIMS/pull/1484
    from bika.lims.upgrade import skip_pre315
    if skip_pre315(aq_parent(aq_inner(tool))):
        return True

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    typestool = getToolByName(portal, 'portal_types')

    # update affected tools
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'controlpanel')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'factorytool')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'propertiestool')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow')

    # Add the object to bika_setup
    try:
        typestool.constructContent(type_name="SupplyOrderFolder",
                               container=portal.bika_setup,
                               id='bika_arpriorities',
                               title='AR Priorities')
        obj = portal.bika_setup.bika_arpriorities
        obj.unmarkCreationFlag()
        obj.reindexObject()
    except BadRequest:
        # folder already exists
        pass

    # Some catalog indexes were added or modified
    bsc = getToolByName(portal, 'bika_setup_catalog')
    bsc.addIndex('sortKey', 'FieldIndex')
    bsc.manage_reindexIndex(ids=['sortKey',])

    return True
