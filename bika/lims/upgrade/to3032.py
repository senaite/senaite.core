from Acquisition import aq_parent, aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from zExceptions import BadRequest


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    setup.runImportStepFromProfile(
            'profile-bika.lims:default', 'plone.app.registry')

    return True
