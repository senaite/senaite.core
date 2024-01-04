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
from senaite.app.listing.adapters.workflow import ListingWorkflowTransition
from senaite.app.listing.interfaces import IListingWorkflowTransition
from zope.interface import implementer


@implementer(IListingWorkflowTransition)
class SampleReceiveWorkflowTransition(ListingWorkflowTransition):
    """Adapter to execute the workflow transition "receive" for samples
    """
    def __init__(self, view, context, request):
        super(SampleReceiveWorkflowTransition, self).__init__(
            view, context, request)
        self.back_url = request.get_header("referer")

    def get_redirect_url(self):
        """Redirect after sample receive transition
        """
        if self.is_auto_partition_required():
            # Redirect to the partitioning view
            uid = api.get_uid(self.context)
            url = "{}/partition_magic?uids={}".format(self.back_url, uid)
            return url

        if self.is_auto_print_stickers_enabled():
            # Redirect to the auto-print stickers view
            uid = api.get_uid(self.context)
            url = "{}/sticker?autoprint=1&items={}".format(self.back_url, uid)
            return url

        # return default value
        return super(SampleReceiveWorkflowTransition, self).get_redirect_url()

    def is_auto_partition_required(self):
        """Returns whether the sample needs to be partitioned
        """
        template = self.context.getTemplate()
        return template and template.getAutoPartition()

    def is_auto_print_stickers_enabled(self):
        """Returns whether the auto print of stickers on reception is enabled
        """
        setup = api.get_setup()
        return "receive" in setup.getAutoPrintStickers()
