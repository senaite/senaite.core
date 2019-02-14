from operator import attrgetter

from bika.lims import api
from bika.lims.browser.workflow import WorkflowActionGenericAdapter
from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING


class WorkflowActionAssignAdapter(WorkflowActionGenericAdapter):
    """Adapter in charge of assignment of analyses into a worksheet
    """

    def __call__(self, action, analyses):

        worksheet = self.context

        # Sort the analyses by AR ID ascending + priority sort key, so the
        # positions of the ARs inside the WS are consistent with ARs order
        sorted_analyses = self.sorted_analyses(analyses)

        # Add analyses into the worksheet
        self.context.addAnalyses(sorted_analyses)

        # Redirect the user to success page
        return self.success([worksheet])

    def sorted_analyses(self, analyses):
        """Sort the analyses by AR ID ascending and subsorted by priority
        sortkey within the AR they belong to
        """
        analysis_uids = map(api.get_uid, analyses)
        catalog = api.get_tool(CATALOG_ANALYSIS_LISTING)
        brains = catalog({
            "UID": analysis_uids,
            "sort_on": "getRequestID"})

        # Now, we need the analyses within a request ID to be sorted by
        # sortkey (sortable_title index), so it will appear in the same
        # order as they appear in Analyses list from AR view
        curr_arid = None
        curr_brains = []
        sorted_brains = []
        for brain in brains:
            arid = brain.getRequestID
            if curr_arid != arid:
                # Sort the brains we've collected until now, that
                # belong to the same Analysis Request
                curr_brains.sort(key=attrgetter("getPrioritySortkey"))
                sorted_brains.extend(curr_brains)
                curr_arid = arid
                curr_brains = []

            # Now we are inside the same AR
            curr_brains.append(brain)
            continue

        # Sort the last set of brains we've collected
        curr_brains.sort(key=attrgetter('getPrioritySortkey'))
        sorted_brains.extend(curr_brains)
        return map(api.get_object, sorted_brains)
