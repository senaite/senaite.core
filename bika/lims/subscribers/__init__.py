from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
import App
import transaction

def skip(instance, action, peek = False, unskip = False):
    """Returns True if the transition is to be SKIPPED
    peek - True just checks the value, does not set.
    unskip - remove skip key (for manual overrides)
    """
    uid = callable(instance.UID) and instance.UID() or instance.UID
    skipkey = "%s_%s" % (uid, action)
    if not instance.REQUEST.has_key('workflow_skiplist'):
        if not peek and not unskip:
            instance.REQUEST['workflow_skiplist'] = [skipkey, ]
    else:
        if skipkey in instance.REQUEST['workflow_skiplist']:
            if unskip:
                instance.REQUEST['workflow_skiplist'].remove(skipkey)
            else:
                return True
        else:
            if not peek and not unskip:
                instance.REQUEST["workflow_skiplist"].append(skipkey)

def doActionFor(instance, action_id):
    workflow = getToolByName(instance, "portal_workflow")
    if not skip(instance, action_id, peek=True):
        try:
            workflow.doActionFor(instance, action_id)
        except WorkflowException:
            pass
