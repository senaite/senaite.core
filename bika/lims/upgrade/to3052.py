from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.lims.permissions import *
from bika.lims.setuphandlers import BikaGenerator
from bika.lims import logger

def upgrade(tool):
    """  stickers
    """
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    
    prt = portal.bika_setup.AutoPrintLabels
    portal.bika_setup.setAutoPrintStickers(prt)

    size = portal.bika_setup.AutoLabelSize
    portal.bika_setup.setAutoStickerTemplate('bika.lims:sticker_%s.pt' %size)

    return True
