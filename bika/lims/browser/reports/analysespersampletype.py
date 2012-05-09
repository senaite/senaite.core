from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.client import ClientSamplesView
from bika.lims.utils import TimeOrDate
from bika.lims.interfaces import IReports
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
import json
import plone

class AnalysesPerSampleType(BrowserView):
    """ stuff
    """
    implements(IViewView)
    template = ViewPageTemplateFile("analysespersampletype.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.TimeOrDate = TimeOrDate

    def __call__(self):
        # get all the data into datalines

        sc = getToolByName(self.context, 'bika_setup_catalog')
        bc = getToolByName(self.context, 'bika_analysis_catalog')
        rc = getToolByName(self.context, 'reference_catalog')
        self.report_content = {}
        parms = {}
        count_all = 0
        query = {'portal_type': 'Analysis'}
        if self.request.form.has_key('getClientUID'):
            client_uid = self.request.form['getClientUID']
            query['getClientUID'] = client_uid
            client = rc.lookupObject(client_uid)
            parms['client'] = client.Title()
        else:
            parms['client'] = 'None'

        date_query = formatDateQuery(self.context, 'st_DateRequested')
        if date_query:
            query['created'] = date_query
        parms['daterequested'] = date_query

        if self.request.form.has_key('review_state'):
            query['review_state'] = self.request.form['review_state']
            parms['review_state'] = self.request.form['review_state']
        else:
            parms['review_state'] = None

        if self.request.form.has_key('cancellation_state'):
            query['cancellation_state'] = self.request.form['cancellation_state']
            parms['cancellation_state'] = self.request.form['cancellation_state']
        else:
            parms['cancellation_state'] = None


        if self.request.form.has_key('ws_review_state'):
            query['worksheetanalysis_review_state'] = self.request.form['ws_review_state']
            parms['ws_review_state'] = self.request.form['ws_review_state']
        else:
            parms['ws_review_state'] = None



        datalines = []
        for cat in sc(portal_type="AnalysisCategory",
                        sort_on='sortable_title'):
            service_data = []
            for service in sc(portal_type="AnalysisService",
                            getCategoryUID = cat.UID,
                            sort_on='sortable_title'):
                query['getServiceUID'] = service.UID
                analyses = bc(query)
                count_analyses = len(analyses)
                service_data.append([service.Title, count_analyses])
                count_all += count_analyses

            datalines.append([cat.Title, service_data])




        self.report_content = {
                'parms': parms,
                'datalines': datalines,
                'total': count_all}


        return self.template()


