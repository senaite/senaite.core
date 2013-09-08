from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims.permissions import *
from Products.Archetypes import PloneMessageFactory as _p
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName

import logging


class Empty:
    pass


def upgrade(tool):
    """
    issue #948 requires permission updates
    """

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    typestool = getToolByName(portal, 'portal_types')

    # update affected tools
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')

    # re-import default permissions
    from bika.lims.setuphandlers import BikaGenerator
    gen = BikaGenerator()
    gen.setupPermissions(portal)

    return True

