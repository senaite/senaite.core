# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from operator import itemgetter

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.analyses.view import AnalysesView
from bika.lims.config import QCANALYSIS_TYPES


class QCAnalysesView(AnalysesView):
    """Renders the table of QC Analyses performed related to an AR.

    Different AR analyses can be achieved inside different worksheets, and each
    one of these can have different QC Analyses. This table only lists the QC
    Analyses performed in those worksheets in which the current AR has, at
    least, one analysis assigned and if the QC analysis services match with
    those from the current AR.
    """

    def __init__(self, context, request, **kwargs):
        AnalysesView.__init__(self, context, request, **kwargs)
        self.columns['getReferenceAnalysesGroupID'] = {
            'title': _('QC Sample ID'),
            'sortable': False}
        self.columns['Worksheet'] = {'title': _('Worksheet'),
                                     'sortable': False}
        self.review_states[0]['columns'] = ['Service',
                                            'Worksheet',
                                            'getReferenceAnalysesGroupID',
                                            'Partition',
                                            'Method',
                                            'Instrument',
                                            'Result',
                                            'Uncertainty',
                                            'CaptureDate',
                                            'DueDate',
                                            'state_title']

        qcanalyses = context.getQCAnalyses()
        asuids = [an.UID() for an in qcanalyses]
        self.contentFilter = {'UID': asuids,
                              'sort_on': 'getId'}
        self.icon = self.portal_url + \
            "/++resource++bika.lims.images/referencesample.png"

    # TODO-performance: Do not use object. Using brain, use meta_type in
    # order to get the object's type
    def folderitem(self, obj, item, index):
        """Prepare a data item for the listing.

        :param obj: The catalog brain or content object
        :param item: Listing item (dictionary)
        :param index: Index of the listing item
        :returns: Augmented listing data item
        """

        obj = obj.getObject()
        # Group items by RefSample - Worksheet - Position
        wss = obj.getBackReferences('WorksheetAnalysis')
        wsid = wss[0].id if wss and len(wss) > 0 else ''
        wshref = wss[0].absolute_url() if wss and len(wss) > 0 else None
        if wshref:
            item['replace']['Worksheet'] = "<a href='%s'>%s</a>" % (
                wshref, wsid)

        imgtype = ""
        if obj.portal_type == 'ReferenceAnalysis':
            antype = QCANALYSIS_TYPES.getValue(obj.getReferenceType())
            if obj.getReferenceType() == 'c':
                imgtype = "<img title='%s' " \
                          "src='%s/++resource++bika.lims.images/control.png" \
                          "'/>&nbsp;" % (
                              antype, self.context.absolute_url())
            if obj.getReferenceType() == 'b':
                imgtype = "<img title='%s' " \
                          "src='%s/++resource++bika.lims.images/blank.png" \
                          "'/>&nbsp;" % (
                              antype, self.context.absolute_url())
            item['replace']['Partition'] = "<a href='%s'>%s</a>" % (
                obj.aq_parent.absolute_url(), obj.aq_parent.id)
        elif obj.portal_type == 'DuplicateAnalysis':
            antype = QCANALYSIS_TYPES.getValue('d')
            imgtype = "<img title='%s' " \
                      "src='%s/++resource++bika.lims.images/duplicate.png" \
                      "'/>&nbsp;" % (
                          antype, self.context.absolute_url())
            item['sortcode'] = '%s_%s' % (obj.getSample().id, obj.getKeyword())

        item['before']['Service'] = imgtype
        item['sortcode'] = '%s_%s' % (obj.getReferenceAnalysesGroupID(),
                                      obj.getKeyword())
        return item

    def folderitems(self):
        items = AnalysesView.folderitems(self)
        # Sort items
        items = sorted(items, key=itemgetter('sortcode'))
        return items
