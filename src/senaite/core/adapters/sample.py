# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

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


@implementer(IWorkflowActionUIDsAdapter)
class WorkflowActionMultiResultsAdapter(RequestContextAware):
    """Redirects to multi results view
    """

    def __call__(self, action, uids):
        """Redirects the user to the multi results form
        """
        context_url = api.get_url(self.context)
        url = "{}/multi_results?uids={}".format(
            context_url, ",".join(uids))
        return self.redirect(redirect_url=url)
