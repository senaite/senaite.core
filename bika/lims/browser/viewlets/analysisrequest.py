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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import ViewletBase
from bika.lims import api


class InvalidAnalysisRequestViewlet(ViewletBase):
    """ Current Analysis Request is invalid and display the link to the retest
    """
    template = ViewPageTemplateFile("templates/invalid_ar_viewlet.pt")


class RetestAnalysisRequestViewlet(ViewletBase):
    """ Current Analysis Request is a retest. Display the link to the invalid
    """
    template = ViewPageTemplateFile("templates/retest_ar_viewlet.pt")


class PrimaryAnalysisRequestViewlet(ViewletBase):
    """ Current Analysis Request is a primary. Display links to partitions
    """
    template = ViewPageTemplateFile("templates/primary_ar_viewlet.pt")

    def get_partitions(self):
        """Returns whether this viewlet is visible or not
        """
        # If current user is a client contact, rely on Setup's ShowPartitions
        if api.get_current_client():
            if not api.get_setup().getShowPartitions():
                return []
        return self.context.getDescendants()


class PartitionAnalysisRequestViewlet(ViewletBase):
    """ Current Analysis Request is a partition. Display the link to primary
    """
    template = ViewPageTemplateFile("templates/partition_ar_viewlet.pt")


class SecondaryAnalysisRequestViewlet(ViewletBase):
    """ Current Analysis Request is a secondary. Display the link to primary
    """
    template = ViewPageTemplateFile("templates/secondary_ar_viewlet.pt")


class RejectedAnalysisRequestViewlet(ViewletBase):
    """Current ANalysis Request was rejected. Display the reasons
    """
    template = ViewPageTemplateFile("templates/rejected_ar_viewlet.pt")
