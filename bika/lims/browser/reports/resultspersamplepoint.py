from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import formatDateQuery, formatDateParms
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
import json
import plone

class ResultsPerSamplePoint(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/report_out.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

    def __call__(self):
        # get all the data into datalines

        bsc = getToolByName(self.context, 'bika_setup_catalog')
        bac = getToolByName(self.context, 'bika_analysis_catalog')
        rc = getToolByName(self.context, 'reference_catalog')
        localTimeFormat = self.context.portal_properties.site_properties.getProperty('localTimeFormat')
        self.report_content = {}
        parm_lines = {}
        parms = []
        headings = {}
        headings['header'] = _("Results per sample point")
        headings['subheader'] = _("Analysis results per sample point and analysis service")

        count_all = 0

        query = {'portal_type' : "Analysis",
                 'review_state': 'published',
                 'sort_on'     : 'getDateAnalysisPublished'}

        if self.request.form.has_key('getSamplePointUID'):
            sp_uid = self.request.form['getSamplePointUID']
            query['getSamplePointUID'] = sp_uid
            sp = rc.lookupObject(sp_uid)
            sp_title = sp.Title()
        else:
            sp_title = 'Undefined'
        parms.append(
            { 'title': _('Sample point'),
             'value': sp_title,
             'type': 'text'})

        if self.request.form.has_key('getSampleTypeUID'):
            st_uid = self.request.form['getSampleTypeUID']
            query['getSampleTypeUID'] = st_uid
            st = rc.lookupObject(st_uid)
            st_title = st.Title()
        else:
            st_title = 'Undefined'
        parms.append(
            { 'title': _('Sample type'),
             'value': st_title,
             'type': 'text'})

        service_uids = []
        if self.request.form.has_key('getServiceUID'):
            service_uid = self.request.form['getServiceUID']
            query['getServiceUID'] = service_uid
        if type(service_uid) == str:
            # a single service was selected
            service_uids.append(service_uid)
            no_services = 1
        else:
            # multiple services were selected
            service_uids = list(service_uid)
            no_services = len(service_uids)

        service_titles = []
        service_values = {}
        service_counts = {}
        service_oor = {}            # out of range
        service_joor = {}           # just out of range
        service_keys = {}
        for service_uid in service_uids:
            service = rc.lookupObject(service_uid)
            service_titles.append('%s  (%s)' \
                %(service.Title(), service.getUnit()))
            service_values[service_uid] = []
            service_counts[service_uid] = 0
            service_oor[service_uid] = 0
            service_joor[service_uid] = 0
            service_keys[service_uid] = service.getKeyword()


        date_query = formatDateQuery(self.context, 'DateAnalysisPublished')
        if date_query:
            query['getDateAnalysisPublished'] = date_query
            published = formatDateParms(self.context, 'DateAnalysisPublished')
        else:
            published = 'Undefined'
        parms.append(
            { 'title': _('Published'),
             'value': published,
             'type': 'text'})

        if self.request.form.has_key('cancellation_state'):
            query['cancellation_state'] = self.request.form['cancellation_state']
            cancellation_state = workflow.getTitleForStateOnType(
                        self.request.form['cancellation_state'], 'Analysis')
        else:
            cancellation_state = 'Undefined'
        parms.append(
            { 'title': _('Active'),
             'value': cancellation_state,
             'type': 'text'})



        if self.request.form.has_key('ws_review_state'):
            query['worksheetanalysis_review_state'] = self.request.form['ws_review_state']
            ws_review_state = workflow.getTitleForStateOnType(
                        self.request.form['ws_review_state'], 'Analysis')
        else:
            ws_review_state = 'Undefined'
        parms.append(
            { 'title': _('Assigned to worksheet'),
             'value': ws_review_state,
             'type': 'text'})

        # get the lab specs for these services
        specs = {}
        owner_uid = self.context.bika_setup.bika_analysisspecs.UID()
        proxies = bsc(portal_type = 'AnalysisSpec',
                      getSampleTypeUID = st_uid,
                      getClientUID = owner_uid)
        if len(proxies) > 0:
            spec_object = proxies[0].getObject()
            results_range = spec_object.getResultsRangeDict()
            for service_uid in service_uids:
                keyword = service_keys[service_uid]
                if results_range.has_key(keyword):
                    specs[service_uid] = results_range[keyword]


        # and now lets do the actual report lines
        formats = {'columns': no_services + 1,
                   'col_heads': [' ',] + service_titles,
                   'class': '',
                  }

        datalines = []
        dataline = []

        dataline = [{'value':'Specification minimum',
                    'class':'colhead'}, ]
        for service_uid in service_uids:
            dataline.append({'value': specs[service_uid]['min'],
                             'class':'colhead number'})
        datalines.append(dataline)

        dataline = [{'value':'Specification maximum',
                    'class':'colhead'}, ]
        for service_uid in service_uids:
            dataline.append({'value': specs[service_uid]['max'],
                             'class':'colhead number'})
        datalines.append(dataline)

        current = None
        first = True
        def loadlines():
            more = True
            while more:
                thisline = [{'value': current},]
                more = False
                for service_uid in service_uids:
                    if service_values[service_uid]:
                        item = service_values[service_uid].pop(0)
                        if service_values[service_uid]:
                            more = True
                        thisline.append(item)
                    else:
                        thisline.append({'value': '-'})
                datalines.append(thisline)

        joor_img = '++resource++bika.lims.images/warning.png'
        oor_img  = '++resource++bika.lims.images/exclamation.png'
        for a_proxy in bac(query):
            analysis = a_proxy.getObject()
            this_service = analysis.getServiceUID()
            pubdate = analysis.getDateAnalysisPublished()
            published = pubdate.strftime('%d %b %Y')
            if first:
                current = published
                first = False
            if published != current:
                # print the previous date
                loadlines()
                current = published

            if analysis.getResult():
                try:
                    result = float(analysis.getResult())
                except:
                    continue

            dataitem = {'value': analysis.getResult(),
                        'class': 'number'}

            # check if in range
            if specs.has_key(this_service):
                spec_min = float(specs[this_service]['min'])
                spec_max = float(specs[this_service]['max'])
                spec_error = float(specs[this_service]['error'])
                if spec_min < result < spec_max:
                    pass
                else:
                    # check if in shoulder: out of range,
                    # but in acceptable error percentage
                    error_amount = (result / 100) * spec_error
                    error_min = result - error_amount
                    error_max = result + error_amount
                    if ((result < spec_min) and (error_max >= spec_min)) or \
                        ((result > spec_max) and (error_min <= spec_max)):
                        dataitem['img_before'] = joor_img
                        service_joor[this_service] += 1
                    else:
                        dataitem['img_before'] = oor_img
                        service_oor[this_service] += 1

            service_values[this_service].append(dataitem)
            service_counts[this_service] += 1

        # include the last one
        loadlines()

        # footer data
        footlines = []
        footline = []
        footitem = {'value': _('Total analyses out of range'),
                    'colspan': 1,
                    'class': 'total_label'}
        footline.append(footitem)
        for service_uid in service_uids:
            footitem = {'value': service_oor[service_uid],
                        'class': 'number'}
            footline.append(footitem)

        footlines.append(footline)

        footline = []
        footitem = {'value': _('Total analyses within error range'),
                    'colspan': 1,
                    'class': 'total_label'}
        footline.append(footitem)
        for service_uid in service_uids:
            footitem = {'value': service_joor[service_uid],
                        'class': 'number'}
            footline.append(footitem)
        footlines.append(footline)

        footline = []
        footitem = {'value': _('Total number of analyses'),
                    'colspan': 1,
                    'class': 'total_label'}
        footline.append(footitem)
        for service_uid in service_uids:
            footitem = {'value': service_counts[service_uid],
                        'class': 'number'}
            footline.append(footitem)
        footlines.append(footline)



        self.report_content = {
                'headings': headings,
                'parms': parms,
                'formats': formats,
                'datalines': datalines,
                'footings': footlines}


        return self.template()



