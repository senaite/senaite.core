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

from bika.lims.interfaces import IAnalysisRequest
from bika.lims.interfaces import IJSONReadExtender
from bika.lims.jsonapi import get_include_fields
from bika.lims.jsonapi import load_brain_metadata
from bika.lims.jsonapi import load_field_values
from bika.lims.vocabularies import CatalogVocabulary
from bika.lims.workflow import get_workflow_actions
from invoice import InvoiceCreate
from zope.component import adapts
from zope.interface import implements

# This AnalysisRequestViewView import must be here, above all the ones that are
# now below it.  Don't reorganise imports carelessly without taking care to read
# this comment twice.
from .view import AnalysisRequestViewView

from .add2 import AnalysisRequestAddView  # noqa: F401
from .add2 import AnalysisRequestManageView  # noqa: F401
from .add2 import ajaxAnalysisRequestAddView  # noqa: F401
from .analysisrequests import AnalysisRequestsView
from .invoice import InvoicePrintView
from .invoice import InvoiceView
from .manage_analyses import AnalysisRequestAnalysesView
from .manage_results import AnalysisRequestManageResultsView
from .published_results import AnalysisRequestPublishedResults


class ClientContactVocabularyFactory(CatalogVocabulary):

    def __call__(self):
        parent = self.context.aq_parent
        return super(ClientContactVocabularyFactory, self).__call__(
            portal_type='Contact',
            path={'query': "/".join(parent.getPhysicalPath()),
                  'level': 0}
        )


class JSONReadExtender(object):

    """- Adds the full details of all analyses to the AR.Analyses field
    """

    implements(IJSONReadExtender)
    adapts(IAnalysisRequest)

    def __init__(self, context):
        self.context = context

    def ar_analysis_values(self):
        ret = []
        analyses = self.context.getAnalyses(is_active=True)
        for proxy in analyses:
            analysis = proxy.getObject()
            if proxy.review_state == 'retracted':
                # these are scraped up when Retested analyses are found below.
                continue
            # things that are manually inserted into the analysis.
            # These things will be included even if they are not present in
            # include_fields in the request.
            method = analysis.getMethod()
            analysis_data = {
                "Uncertainty": analysis.getUncertainty(),
                "Method": method.Title() if method else '',
                "Unit": analysis.getUnit(),
            }
            # Place all schema fields ino the result.
            analysis_data.update(load_brain_metadata(proxy, []))
            # Place all schema fields ino the result.
            analysis_data.update(load_field_values(analysis, []))
            # call any adapters that care to modify the Analysis data.
            # adapters = getAdapters((analysis, ), IJSONReadExtender)
            # for name, adapter in adapters:
            #     adapter(request, analysis_data)
            if not self.include_fields or "transitions" in self.include_fields:
                analysis_data['transitions'] = get_workflow_actions(analysis)
            retest_of = analysis.getRetestOf()
            if retest_of:
                prevs = [{'created': str(retest_of.created()),
                          'Result': retest_of.getResult(),
                          'InterimFields': retest_of.getInterimFields()}]
                analysis_data['Previous Results'] = prevs
            ret.append(analysis_data)
        return ret

    def __call__(self, request, data):
        self.request = request
        self.include_fields = get_include_fields(request)
        if not self.include_fields or "Analyses" in self.include_fields:
            data['Analyses'] = self.ar_analysis_values()


class mailto_link_from_contacts(object):
    """Custom header table field adapter

    see: bika.lims.browser.header_table
    """

    def __init__(self, context):
        self.context = context

    def __call__(self, field):
        contacts = field.get(self.context)
        if not type(contacts) in (list, tuple):
            contacts = [contacts, ]
        ret = []
        for contact in contacts:
            if contact:
                mailto = "<a href='mailto:%s'>%s</a>" % (
                    contact.getEmailAddress(), contact.getFullname())
                ret.append(mailto)
        return ",".join(ret)


class mailto_link_from_ccemails(object):
    """Custom header table field adapter

    see: bika.lims.browser.header_table
    """

    def __init__(self, context):
        self.context = context

    def __call__(self, field):
        ccemails = field.get(self.context)
        addresses = ccemails.split(",")
        ret = []
        for address in addresses:
            address = address.strip()
            mailto = "<a href='mailto:%s'>%s</a>" % (
                address, address)
            ret.append(mailto)
        return ",".join(ret)
