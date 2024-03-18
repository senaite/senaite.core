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
class AnalysisRetractAdapter(ListingWorkflowTransition):

    def get_uids(self):
        """Return the uids affected by the retract transition
        """
        retest_uid = self.context.getRawRetest()
        uids = [api.get_uid(self.context), retest_uid]
        return filter(None, uids)


@implementer(IListingWorkflowTransition)
class AnalysisRetestAdapter(ListingWorkflowTransition):

    def get_uids(self):
        """Return the uids affected by the retest transition
        """
        retest_uid = self.context.getRawRetest()
        uids = [api.get_uid(self.context), retest_uid]
        return filter(None, uids)
