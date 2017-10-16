import transaction
from plone.api.portal import get_tool

from bika.lims import logger
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from .analyses import commit_action


def set_ar_departments():
    """
    Some of old Analysis Request may not have Departments assigned. This task
    will assign their departments according to their 'analyses'.
    :return: boolean - success state of the process.
    """

    ar_catalog = get_tool(CATALOG_ANALYSIS_REQUEST_LISTING)
    # Getting all Analysis Requests to walk through
    ar_brains = ar_catalog()
    total_ars = len(ar_brains)
    total_iterated = 0
    logger.info("Analysis Requests to walk over: {}".format(total_ars))
    total_modified = 0
    for ar_brain in ar_brains:
        if ar_brain.getDepartmentUIDs:
            continue
        ar = ar_brain.getObject()
        ans = ar.getAnalyses()
        for an_brain in ans:
            dep = None
            an = an_brain.getObject()
            dep = an.getAnalysisService().getDepartment()
            if dep:
                an.setDepartment(dep)
                an.reindexObject()

        ar.reindexObject()
        total_modified = total_modified+1
        total_iterated = commit_action(
            total_ars, total_iterated, total_modified)
    transaction.commit()
    logger.info("AR Department assignment is finished. Total # of modified ARs: \
                {0}".format(str(total_modified)))
    return True
