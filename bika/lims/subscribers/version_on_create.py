from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
import transaction

def ObjectInitializedEventHandler(obj, event):
    pr = getToolByName(obj, 'portal_repository')
    pr.applyVersionControl(obj, comment=_("Initial revision"))
