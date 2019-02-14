# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import collections

from bika.lims import PMF
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.api import get_object_by_uid
from bika.lims.workflow import ActionHandlerPool
from bika.lims.workflow import doActionFor
from senaite.core.listing import ListingView


class WorkflowAction:
    """Workflow actions taken in any Bika contextAnalysisRequest context

    This function provides the default behaviour for workflow actions
    invoked from bika_listing tables.

    Some actions (eg, AR copy_to_new) can be invoked from multiple contexts.
    In that case, I will begin to register their handlers here.
    XXX WorkflowAction handlers should be simple adapters.
    """

    def __init__(self, context, request):
        self.destination_url = ""
        self.context = context
        self.request = request
        self.back_url = self.context.absolute_url()
        # Save context UID for benefit of event subscribers.
        self.request['context_uid'] = hasattr(self.context, 'UID') and \
            self.context.UID() or ''
        self.portal = api.get_portal()
        self.addPortalMessage = self.context.plone_utils.addPortalMessage

    def __call__(self):

        return self.redirect(message="bika_listing.WorkflowAction",
                             level="error")

        request = self.request


class BikaListingView(ListingView):
    """BBB: Base View for Table Listings

    Please use `senaite.core.listing.ListingView` instead
    https://github.com/senaite/senaite.core/pull/1226
    """
