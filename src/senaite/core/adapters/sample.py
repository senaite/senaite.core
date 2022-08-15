# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims.browser.workflow import RequestContextAware
from bika.lims.browser.workflow import WorkflowActionGenericAdapter
from bika.lims.interfaces import IWorkflowActionUIDsAdapter
from zope.interface import implementer


@implementer(IWorkflowActionUIDsAdapter)
class WorkflowActionDispatchAdapter(RequestContextAware):
    """Adapter in charge of Sample "dispatch" action
    """

    def __call__(self, action, uids):
        """Redirects the user to the dispatch form
        """
        url = "{}/dispatch_samples?uids={}".format(
            api.get_url(self.context), ",".join(uids))
        return self.redirect(redirect_url=url)


class WorkflowActionMultiResultsAdapter(WorkflowActionGenericAdapter):
    """Multi results WF transition adapter
    """

    def __call__(self, action, objects):
        """Redirects the user to the multi results form
        """
        uids = map(api.get_uid, objects)
        url = "{}/multi_results?uids={}".format(
            api.get_url(self.context), ",".join(uids))
        return self.redirect(redirect_url=url)
