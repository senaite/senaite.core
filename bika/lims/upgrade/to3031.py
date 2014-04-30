from Products.CMFPlone.utils import _createObjectByType
from zExceptions import BadRequest


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
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
