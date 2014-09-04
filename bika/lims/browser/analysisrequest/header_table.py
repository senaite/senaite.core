from Products.CMFCore.utils import getToolByName
from bika.lims.interfaces import IHeaderTableFieldRenderer
from zope.interface import implements


class PreparationWorkflow(object):
    implements(IHeaderTableFieldRenderer)

    def __init__(self, context):
        self.context = context

    def __call__(self, field):
        wf_id = field.get(self.context)
        if not wf_id:
            return ""
        wf_tool = getToolByName(self.context, 'portal_workflow')
        workflow = wf_tool.getWorkflowById(wf_id)
        if not workflow:
            return ""
        return workflow.title
