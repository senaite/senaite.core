from Acquisition import aq_parent, aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from zExceptions import BadRequest


def upgrade(tool):
    # Hack prevent out-of-date upgrading
    # Related: PR #1484
    # https://github.com/bikalabs/Bika-LIMS/pull/1484
    from bika.lims.upgrade import skip_pre315
    if skip_pre315(aq_parent(aq_inner(tool))):
        return True

    portal = aq_parent(aq_inner(tool))
    at = getToolByName(portal, 'archetype_tool')
    at.setCatalogsByType('SubGroup', ['bika_setup_catalog', ])
    setup = portal.portal_setup
    setup.runImportStepFromProfile('profile-bika.lims:default', 'controlpanel')

    try:
        _createObjectByType("SubGroups", portal.bika_setup, "bika_subgroups",
                            title="Sub-groups")
        obj = portal.bika_setup.bika_subgroups
        obj.unmarkCreationFlag()
        obj.reindexObject()
    except BadRequest:
        # folder already exists
        pass

    return True
