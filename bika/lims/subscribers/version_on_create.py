from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
import transaction

def ObjectInitializedEventHandler(obj, event):
    # attempt initial save of version aware objects
    pr = getToolByName(obj, 'portal_repository')
    pr.save(obj=obj, comment=_("Initial revision"))
