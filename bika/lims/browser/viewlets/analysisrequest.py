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

from bika.lims import FieldEditSpecification
from bika.lims import api
from bika.lims import logger
from bika.lims.api.security import check_permission
from zope.schema import getFields


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

    def get_primary_bound_fields(self):
        """Returns a list with the names of the fields the current user has
        write priveleges and for which changes in primary sample will apply to
        its descendants too
        """
        bound = []
        schema = api.get_schema(self.context)
        for field in schema.fields():
            if not hasattr(field, "primary_bound"):
                continue

            if not check_permission(field.write_permission, self.context):
                # Current user does not have permission to edit this field
                continue

            if field.primary_bound:
                # Change in this field will populate to partitions
                bound.append(field.widget.label)

        return bound


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


class DetachedPartitionViewlet(ViewletBase):
    """Prints a viewlet that displays the Primary Sample the sample was
    detached from
    """
    template = ViewPageTemplateFile("templates/detached_partition_viewlet.pt")


class ResultsRangesOutOfDateViewlet(ViewletBase):
    """Print a viewlet that displays if results ranges from Sample are different
    from results ranges initially set through Specifications field. If so, this
    means the Specifications initially set have changed since they were set and
    for new analyses, the old specifications will be kept
    """

    def is_specification_editable(self):
        """Returns whether the Specification field is editable or not
        """
        return check_permission(FieldEditSpecification, self.context)

    def is_results_ranges_out_of_date(self):
        """Returns whether the value for ResultsRange field does not match with
        the results ranges that come from the Specification assigned
        """
        sample = self.context
        sample_rr = sample.getResultsRange()
        if not sample_rr:
            # No results ranges set to this Sample, do nothing
            return False

        specifications = sample.getSpecification()
        if not specifications:
            # This should never happen
            logger.error("No specifications, but results ranges set for {}"
                         .format(api.get_id(sample)))
            return False

        # Compare if results ranges are different
        spec_rr = specifications.getResultsRange()
        return sample_rr != spec_rr
