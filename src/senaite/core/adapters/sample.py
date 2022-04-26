# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims.browser.workflow import RequestContextAware
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
