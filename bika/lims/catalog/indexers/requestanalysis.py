from bika.lims import api
from bika.lims.interfaces import IReferenceAnalysis
from bika.lims.interfaces.analysis import IRequestAnalysis
from plone.indexer import indexer


@indexer(IRequestAnalysis)
def getAncestorsUIDs(instance):
    """Returns the UIDs of all the ancestors (Analysis Requests) this analysis
    comes from
    """
    request = instance.getRequest()
    parents = map(lambda ar: api.get_uid(ar), request.getAncestors())
    return [api.get_uid(request)] + parents


@indexer(IRequestAnalysis)
def cancellation_state(instance):
    """Acts as a mask for cancellation_workflow that is not bound to Analysis
    content type. Returns 'active' or 'cancelled'
    """
    if api.get_workflow_status_of(instance) == "cancelled":
        return "cancelled"
    return "active"
