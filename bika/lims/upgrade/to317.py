from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.lims.permissions import *
from bika.lims.setuphandlers import BikaGenerator
from bika.lims import logger

def upgrade(tool):
    """
    Upgrade step required for Bika LIMS 3.1.7
    """

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    setup.runImportStepFromProfile('profile-bika.lims:default', 'jsregistry')

    return True
