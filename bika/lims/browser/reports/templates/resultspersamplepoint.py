from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
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
    template = ViewPageTemplateFile("output_resultspersamplepoint.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

    def error(self, message):
        # Return to the query form and display a message
        self.context.plone_utils.addPortalMessage(message, 'error')
        self.template = ViewPageTemplateFile("reports_qualitycontrol.pt")
        return template()

    def __call__(self):
        bsc = getToolByName(self.context, "bika_setup_catalog")
        bac = getToolByName(self.context, "bika_analysis_catalog")
        rc = getToolByName(self.context, "reference_catalog")
        site_props = self.context.portal_properties.site_properties
        localTimeFormat = site_props.getProperty("localTimeFormat")

        # Parse form criteria

        sp_uid = self.request.form["SamplePointUID"]
        sp_title = rc.lookupObject(sp_uid).Title()

        st_uid = self.request.form["SampleTypeUID"]
        st_title = rc.lookupObject(st_uid).Title()

        if "ServiceUID" not in self.request.form:
            self.error(_("No analysis services were selected."))
        if type(self.request.form["ServiceUID"]) in (list, tuple):
            service_uids = self.request.form["ServiceUID"] # Multiple services
        else:
            service_uids = (self.request.form["ServiceUID"],) # Single service
        services = [rc.lookupObject(s) for s in service_uids]

        self.report_content = {
            # 'parms' is for displaying the selected criteria in the output
            'parms': [
                {'title': _('Sample point'), 'value': sp_title, 'type': 'text'},
                {'title': _('Sample type'), 'value': st_title, 'type': 'text'}
            ],
            'headings': {
                'header': "Results per sample point",
                'subheader': "Analysis results per sample point and analysis service"
            }
        }

        query = {
            "portal_type": "Analysis",
            "getSamplePointUID": sp_uid,
            "getSampleTypeUID": st_uid,
            "getServiceUID": services,
            "sort_on": "sortable_title"
        }





        for service in services:
            uid = services.UID()
            service_titles.append('%s (%s)' % (service.Title(),
                                               service.getUnit()))
            service_values[uid] = []
            service_counts[service_uid] = 0
            service_oor[service_uid] = 0
            service_joor[service_uid] = 0
            service_keys[service_uid] = service.getKeyword()

        date_query = formatDateQuery(self.context, 'DateAnalysisPublished')
        if date_query:
            query['getDateAnalysisPublished'] = date_query
            query['review_state'] = 'published'
            parms.append({
                'title': _('Published'),
                'value': formatDateParms(self.context, 'DateAnalysisPublished'),
                'type': 'text'
            })

        if self.request.form.has_key('cancellation_state'):
            query['cancellation_state'] = self.request.form['cancellation_state']
            cancellation_state = workflow.getTitleForStateOnType(
                        self.request.form['cancellation_state'], 'Analysis')
            parms.append(
                {'title': _('Active'),
                 'value': cancellation_state,
                 'type': 'text'})

        if self.request.form.has_key('ws_review_state'):
            query['worksheetanalysis_review_state'] = self.request.form['ws_review_state']
            ws_review_state = workflow.getTitleForStateOnType(
                        self.request.form['ws_review_state'], 'Analysis')
            parms.append(
                {'title': _('Assigned to worksheet'),
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

        dataline = [{'value':'Specification minimum', 'class':'colhead'}, ]
        for service_uid in service_uids:
            spec = specs.get(service_uid, {'min':''})
            dataline.append({'value': spec['min'], 'class':'colhead number'})
        datalines.append(dataline)

        dataline = [{'value':'Specification maximum', 'class':'colhead'}, ]
        for service_uid in service_uids:
            spec = specs.get(service_uid, {'max':''})
            dataline.append({'value': spec['max'], 'class':'colhead number'})
        datalines.append(dataline)

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


        self.report_content[formats] = formats
        self.report_content['datalines'] = datalines
        self.report_content['footings'] = footlines

        return self.template()



