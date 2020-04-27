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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from collections import OrderedDict

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.analyses.view import AnalysesView
from bika.lims.config import QCANALYSIS_TYPES
from bika.lims.interfaces import IDuplicateAnalysis
from bika.lims.utils import get_image
from bika.lims.utils import get_link


class QCAnalysesView(AnalysesView):
    """Renders the table of QC Analyses performed related to an AR.

    Different AR analyses can be achieved inside different worksheets, and each
    one of these can have different QC Analyses. This table only lists the QC
    Analyses performed in those worksheets in which the current AR has, at
    least, one analysis assigned and if the QC analysis services match with
    those from the current AR.
    """

    def __init__(self, context, request, **kwargs):
        super(QCAnalysesView, self).__init__(context, request, **kwargs)

        icon_path = "/++resource++bika.lims.images/referencesample.png"
        self.icon = "{}{}".format(self.portal_url, icon_path)

        # Add Worksheet and QC Sample ID columns
        new_columns = OrderedDict((
            ("Worksheet", {
                "title": _("Worksheet"),
                "sortable": True,
            }),
            ("getReferenceAnalysesGroupID", {
                "title": _('QC Sample ID'),
                "sortable": False,
            }),
            ("Parent", {
                "title": _("Source"),
                "sortable": False,
            })
        ))
        self.columns.update(new_columns)

        # Remove unnecessary columns
        if "Hidden" in self.columns:
            del(self.columns["Hidden"])

        # Remove filters (Valid, Invalid, All)
        self.review_states = [self.review_states[0]]

        # Apply the columns to all review_states
        for review_state in self.review_states:
            review_state.update({"columns": self.columns.keys()})

    def update(self):
        """Update hook
        """
        super(AnalysesView, self).update()
        # Update the query with the QC Analyses uids
        qc_uids = map(api.get_uid, self.context.getQCAnalyses())
        self.contentFilter.update({
            "UID": qc_uids,
            "portal_type": ["DuplicateAnalysis", "ReferenceAnalysis"],
            "sort_on": "sortable_title"
        })

    def is_analysis_edition_allowed(self, analysis_brain):
        """Overwrite this method to ensure the table is recognized as readonly

        XXX: why is the super method not recognizing `self.allow_edit`?
        """
        return False

    def folderitem(self, obj, item, index):
        item = super(QCAnalysesView, self).folderitem(obj, item, index)

        obj = self.get_object(obj)

        # Fill Worksheet cell
        worksheet = obj.getWorksheet()
        if not worksheet:
            return item

        # Fill the Worksheet cell
        ws_id = api.get_id(worksheet)
        ws_url = api.get_url(worksheet)
        item["replace"]["Worksheet"] = get_link(ws_url, value=ws_id)

        if IDuplicateAnalysis.providedBy(obj):
            an_type = "d"
            img_name = "duplicate.png"
            parent = obj.getRequest()
        else:
            an_type = obj.getReferenceType()
            img_name = an_type == "c" and "control.png" or "blank.png"
            parent = obj.aq_parent

        # Render the image
        an_type = QCANALYSIS_TYPES.getValue(an_type)
        item['before']['Service'] = get_image(img_name, title=an_type)

        # Fill the Parent cell
        parent_url = api.get_url(parent)
        parent_id = api.get_id(parent)
        item["replace"]["Parent"] = get_link(parent_url, value=parent_id)

        return item
