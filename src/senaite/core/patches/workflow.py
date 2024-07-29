# -*- coding: utf-8 -*-

from bika.lims import api


def _reindexWorkflowVariables(self, ob):
    """This function is called by DCWorkflow immediately after the workflow
    action is invoked in WorkflowTool.doActionFor.

    The original function is only responsible of reindexing the variables that
    may have changed due to the transition (e.g review_state) along with
    security-related indexes. However, the original function does two calls
    to reindexObject, one for workflow variables and another one for the
    security-related indexes. Metadata is updated on both calls as well, cause
    those workflow-variables might also be stored as metadata.

    Since quite often the transition involves changes not only in
    workflow-related variables, but to other field values, it becomes almost
    a requirement to always reindex the object after a transition. Therefore,
    we simply do a full reindexObject here instead of taking only some indexes
    into account.
    """
    if api.is_temporary(ob):
        return

    # do a full reindex
    ob.reindexObject()
