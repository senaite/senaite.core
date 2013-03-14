import logging

from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent

from Products.CMFCore import permissions
from bika.lims.permissions import *

from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    portal_catalog = getToolByName(portal, 'portal_catalog')
    typestool = getToolByName(portal, 'portal_types')
    setup = portal.portal_setup

    # We made changes to the workflow.
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow')

    return True
