from AccessControl import ModuleSecurityInfo
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from Products.Archetypes.utils import shasattr
from bika.lims import logger
import transaction

ModuleSecurityInfo('bika.lims.subscribers.objectinitialized').declarePublic('applyVersionControl')
def applyVersionControl(obj, event):
    """ Apply version control to IHistoryAware objects
    """
    pr = getToolByName(obj, 'portal_repository')
    pr.applyVersionControl(obj, comment=_("Initial revision"))
