# coding=utf-8
from bika.lims.utils import t
from operator import itemgetter
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName

import plone
import plone.protect
import json


class GetServices():
    """ When a Category is selected in the add_analyses search screen, this
        function returns a list of services from the selected category.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        return json.dumps([c.Title for c in
                bsc(portal_type = 'AnalysisService',
                   getCategoryTitle = self.request.get('getCategoryTitle', ''),
                   inactive_state = 'active',
                   sort_on = 'sortable_title')])


class AttachAnalyses():
    """ In attachment add form,
        the analyses dropdown combo uses this as source.
        Form is handled by the worksheet ManageResults code
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = 'searchTerm' in self.request and self.request['searchTerm'].lower() or ''
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']
        attachable_states = ('assigned', 'sample_received', 'to_be_verified')
        wf = getToolByName(self.context, 'portal_workflow')
        analysis_to_slot = {}
        for s in self.context.getLayout():
            analysis_to_slot[s['analysis_uid']] = int(s['position'])
        analyses = list(self.context.getAnalyses(full_objects=True))
        # Duplicates belong to the worksheet, so we must add them individually
        for i in self.context.objectValues():
            if i.portal_type == 'DuplicateAnalysis':
                analyses.append(i)
        rows = []
        for analysis in analyses:
            review_state = wf.getInfoFor(analysis, 'review_state', '')
            if analysis.portal_type in ('Analysis', 'DuplicateAnalysis'):
                if review_state not in attachable_states:
                    continue
                parent = analysis.getRequestID()
                service = analysis.getService()
            elif analysis.portal_type == 'ReferenceAnalysis':
                if review_state not in attachable_states:
                    continue
                parent = analysis.aq_parent.Title()
                service = analysis.getService()
            rows.append({'analysis_uid': analysis.UID(),
                         'slot': analysis_to_slot[analysis.UID()],
                         'service': service and service.Title() or '',
                         'parent': parent,
                         'type': analysis.portal_type})

        # if there's a searchTerm supplied, restrict rows to those
        # who contain at least one field that starts with the chars from
        # searchTerm.
        if searchTerm:
            orig_rows = rows
            rows = []
            for row in orig_rows:
                matches = [v for v in row.values()
                           if str(v).lower().startswith(searchTerm)]
                if matches:
                    rows.append(row)

        rows = sorted(rows, cmp=lambda x, y: cmp(x, y), key=itemgetter(sidx and sidx or 'slot'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        start = (int(page)-1) * int(nr_rows)
        end = int(page) * int(nr_rows)
        ret = {'page': page,
               'total': pages,
               'records': len(rows),
               'rows': rows[start:end]}

        return json.dumps(ret)


class SetAnalyst():
    """The Analysis dropdown sets worksheet.Analyst immediately
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        mtool = getToolByName(self, 'portal_membership')
        plone.protect.CheckAuthenticator(self.request)
        plone.protect.PostOnly(self.request)
        value = self.request.get('value', '')
        if not value:
            return
        if not mtool.getMemberById(value):
            return
        self.context.setAnalyst(value)


class SetInstrument():
    """The Instrument dropdown sets worksheet.Instrument immediately
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        plone.protect.CheckAuthenticator(self.request)
        plone.protect.PostOnly(self.request)
        value = self.request.get('value', '')
        if not value:
            raise Exception("Invalid instrument")
        instrument = rc.lookupObject(value)
        if not instrument:
            raise Exception("Unable to lookup instrument")
        self.context.setInstrument(instrument)
