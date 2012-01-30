from AccessControl import ModuleSecurityInfo
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from Products.Archetypes.utils import shasattr
from bika.lims import logger
import transaction

def ObjectModifiedEventHandler(obj, event):
    """ Various types need automation on edit.
    """
    if not hasattr(obj, 'portal_type'):
        return

    if obj.portal_type == 'Calculation':
        # Update historyaware back-references
        backrefs = obj.getBackReferences('AnalysisServiceCalculation')
        for service in backrefs:
            service.setCalculation(obj.UID())

