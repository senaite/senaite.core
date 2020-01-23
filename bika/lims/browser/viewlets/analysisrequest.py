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
    means the Specification initially set has changed since it was assigned to
    the Sample and for new analyses, the ranges defined in the initial
    specification ranges will be used instead of the new ones.
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


class SpecificationNotCompliantViewlet(ViewletBase):
    """Print a viewlet that displays if the sample contains analyses that are
    not compliant with the Specification initially set (stored in Sample's
    ResultsRange field). If so, this means that user changed the results ranges
    of the analyses manually, either by adding new ones or by modifying the
    existing ones via "Manage analyses" view. And results range for those
    analyses are different from the Specification initially set.
    """

    def is_specification_editable(self):
        """Returns whether the Specification field is editable or not
        """
        return check_permission(FieldEditSpecification, self.context)

    def get_non_compliant_analyses(self):
        """Returns the list of analysis keywords from this sample with a
        result range set not compliant with the result range of the Sample
        """
        non_compliant = []
        sample = self.context

        # If no Specification is set, assume is compliant
        specification = sample.getSpecification()
        if not specification:
            return []

        # Get the Sample's ResultsRanges, that are copy of those from the
        # Specification initially set.
        sample_rrs = sample.getResultsRange()
        if not sample_rrs:
            # No results range set at Sample level. Assume is compliant
            return []

        # Create a dict for easy access to results ranges
        sample_rrs = dict(map(lambda rr: (rr["uid"], rr), sample_rrs))

        # Check if the results ranges set to analyses individually remain
        # compliant with the Sample's ResultRange
        analyses = sample.getAnalyses(full_objects=True)
        for analysis in analyses:
            rr = analysis.getResultsRange()
            service_uid = rr.get("uid", None)
            if not api.is_uid(service_uid):
                continue

            sample_rr = sample_rrs.get(service_uid)
            if not sample_rr:
                # This service is not defined in Sample's ResultsRange, we
                # assume this *does not* break the compliance
                continue

            else:
                # Clean-up the result range passed in
                form_rr = self.resolve_result_range(rr, sample_rr)
                if form_rr != sample_rr:
                    # Result range for this service has been changed manually,
                    # it does not match with sample's ResultRange
                    an_title = api.get_title(analysis)
                    keyword = analysis.getKeyword()
                    non_compliant.append("{} ({})".format(an_title, keyword))

        # Return the list of keywords from non-compliant analyses
        return list(set(non_compliant))

    def resolve_result_range(self, result_range, original):
        """Cleans up the result range passed-in to match with same keys as the
        original result range, that presumably comes from a Specification
        """
        if not original:
            return result_range

        # Remove keys-values not present in original
        extra_keys = filter(lambda key: key not in original, result_range)
        for key in extra_keys:
            del result_range[key]

        # Add keys-values not present in current result_range but in original
        for key, val in original.items():
            if key not in result_range:
                result_range[key] = val

        return result_range