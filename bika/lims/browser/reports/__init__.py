from Products.CMFPlone.utils import _createObjectByType
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.reports.selection_macros import SelectionMacrosView
from bika.lims.utils import createPdf
from bika.lims.utils import getUsers, logged_in_client
from bika.lims.utils import isAttributeHidden
from bika.lims.utils import to_unicode as _u
from bika.lims.utils import to_utf8 as _c
from bika.lims.interfaces import IProductivityReport
from bika.lims.interfaces import IQualityControlReport
from bika.lims.interfaces import IAdministrationReport
from DateTime import DateTime
from plone.app.layout.globals.interfaces import IViewView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getAdapters
from zope.interface import implements
import json
import os
import plone


class ProductivityView(BrowserView):

    """ Productivity View form
    """
    implements(IViewView)
    template = ViewPageTemplateFile("templates/productivity.pt")

    def __call__(self):
        self.selection_macros = SelectionMacrosView(self.context, self.request)
        self.icon = self.portal_url + "/++resource++bika.lims.images/report_big.png"
        self.getAnalysts = getUsers(self.context, ['Manager', 'LabManager', 'Analyst'])

        self.additional_reports = []
        adapters = getAdapters((self.context, ), IProductivityReport)
        for name, adapter in adapters:
            report_dict = adapter(self.context, self.request)
            report_dict['id'] = name
            self.additional_reports.append(report_dict)

        return self.template()


class QualityControlView(BrowserView):

    """ QC View form
    """
    implements(IViewView)
    template = ViewPageTemplateFile("templates/qualitycontrol.pt")

    def __call__(self):
        self.selection_macros = SelectionMacrosView(self.context, self.request)
        self.icon = self.portal_url + "/++resource++bika.lims.images/report_big.png"

        self.additional_reports = []
        adapters = getAdapters((self.context, ), IQualityControlReport)
        for name, adapter in adapters:
            report_dict = adapter(self.context, self.request)
            report_dict['id'] = name
            self.additional_reports.append(report_dict)

        return self.template()

    def isSamplePointHidden(self):
        return isAttributeHidden('AnalysisRequest', 'SamplePoint')

class AdministrationView(BrowserView):

    """ Administration View form
    """
    implements(IViewView)
    template = ViewPageTemplateFile("templates/administration.pt")

    def __call__(self):
        self.selection_macros = SelectionMacrosView(self.context, self.request)
        self.icon = self.portal_url + "/++resource++bika.lims.images/report_big.png"

        self.additional_reports = []
        adapters = getAdapters((self.context, ), IAdministrationReport)
        for name, adapter in adapters:
            report_dict = adapter(self.context, self.request)
            report_dict['id'] = name
            self.additional_reports.append(report_dict)

        return self.template()


class ReportHistoryView(BikaListingView):

    """ Report history form
    """
    implements(IViewView)

    def __init__(self, context, request):
        super(ReportHistoryView, self).__init__(context, request)

        self.catalog = "bika_catalog"
        # this will be reset in the call to filter on own reports
        self.contentFilter = {'portal_type': 'Report',
                              'sort_order': 'reverse'}
        self.context_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50

        self.icon = self.portal_url + "/++resource++bika.lims.images/report_big.png"
        self.title = _("Reports")
        self.description = ""

        # this is set up in call where member is authenticated
        self.columns = {}
        self.review_states = []

    def __call__(self):
        this_client = logged_in_client(self.context)
        if this_client:
            self.contentFilter = {
                'portal_type': 'Report',
                'getClientUID': this_client.UID(),
                'sort_order': 'reverse'}
            self.columns = {
                'Title': {'title': _('Title')},
                'FileSize': {'title': _('Size')},
                'Created': {'title': _('Created')},
                'By': {'title': _('By')}, }
            self.review_states = [
                {'id': 'default',
                 'title': 'All',
                 'contentFilter': {},
                 'columns': ['Title',
                             'FileSize',
                             'Created',
                             'By']},
            ]
        else:
            self.contentFilter = {
                'portal_type': 'Report',
                'sort_order': 'reverse'}

            self.columns = {
                'Client': {'title': _('Client')},
                'Title': {'title': _('Report Type')},
                'FileSize': {'title': _('Size')},
                'Created': {'title': _('Created')},
                'By': {'title': _('By')},
            }
            self.review_states = [
                {'id': 'default',
                 'title': 'All',
                 'contentFilter': {},
                 'columns': ['Client',
                             'Title',
                             'FileSize',
                             'Created',
                             'By']},
            ]

        return super(ReportHistoryView, self).__call__()

    def lookupMime(self, name):
        mimetool = getToolByName(self, 'mimetypes_registry')
        mimetypes = mimetool.lookup(name)
        if len(mimetypes):
            return mimetypes[0].name()
        else:
            return name

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        props = self.context.portal_properties.site_properties
        for x in range(len(items)):
            if 'obj' not in items[x]:
                continue
            obj = items[x]['obj']
            obj_url = obj.absolute_url()
            file = obj.getReportFile()
            icon = file.getBestIcon()

            items[x]['Client'] = ''
            client = obj.getClient()
            if client:
                items[x]['replace']['Client'] = "<a href='%s'>%s</a>" % \
                    (client.absolute_url(), client.Title())
            items[x]['FileSize'] = '%sKb' % (file.get_size() / 1024)
            items[x]['Created'] = self.ulocalized_time(obj.created())
            items[x]['By'] = self.user_fullname(obj.Creator())

            items[x]['replace']['Title'] = \
                 "<a href='%s/at_download/ReportFile'>%s</a>" % \
                 (obj_url, items[x]['Title'])
        return items


class SubmitForm(BrowserView):

    """ Redirect to specific report
    """
    implements(IViewView)
    frame_template = ViewPageTemplateFile("templates/report_frame.pt")
    # default and errors use this template:
    template = ViewPageTemplateFile("templates/productivity.pt")

    def __call__(self):
        """Create and render selected report
        """

        # if there's an error, we return productivity.pt which requires these.
        self.selection_macros = SelectionMacrosView(self.context, self.request)
        self.additional_reports = []
        adapters = getAdapters((self.context, ), IProductivityReport)
        for name, adapter in adapters:
            report_dict = adapter(self.context, self.request)
            report_dict['id'] = name
            self.additional_reports.append(report_dict)

        report_id = self.request.get('report_id', '')
        if not report_id:
            message = "No report specified in request"
            self.logger.error(message)
            self.context.plone_utils.addPortalMessage(message, 'error')
            return self.template()

        self.date = DateTime()
        username = self.context.portal_membership.getAuthenticatedMember().getUserName()
        self.reporter = self.user_fullname(username)
        self.reporter_email = self.user_email(username)

        # signature image
        self.reporter_signature = ""
        c = [x for x in self.bika_setup_catalog(portal_type='LabContact')
             if x.getObject().getUsername() == username]
        if c:
            sf = c[0].getObject().getSignature()
            if sf:
                self.reporter_signature = sf.absolute_url() + "/Signature"

        lab = self.context.bika_setup.laboratory
        self.laboratory = lab
        self.lab_title = lab.getName()
        self.lab_address = lab.getPrintAddress()
        self.lab_email = lab.getEmailAddress()
        self.lab_url = lab.getLabURL()

        client = logged_in_client(self.context)
        if client:
            clientuid = client.UID()
            self.client_title = client.Title()
            self.client_address = client.getPrintAddress()
        else:
            clientuid = None
            self.client_title = None
            self.client_address = None

        # Render form output

        # the report can add file names to this list; they will be deleted
        # once the PDF has been generated.  temporary plot image files, etc.
        self.request['to_remove'] = []

        if "report_module" in self.request:
            module = self.request["report_module"]
        else:
            module = "bika.lims.browser.reports.%s" % report_id
        try:
            exec("from %s import Report" % module)
            # required during error redirect: the report must have a copy of
            # additional_reports, because it is used as a surrogate view.
            Report.additional_reports = self.additional_reports
        except ImportError:
            message = "Report %s.Report not found (shouldn't happen)" % module
            self.logger.error(message)
            self.context.plone_utils.addPortalMessage(message, 'error')
            return self.template()

        # Report must return dict with:
        # - report_title - title string for pdf/history listing
        # - report_data - rendered report
        output = Report(self.context, self.request)()

        # if CSV output is chosen, report returns None
        if not output:
            return

        if type(output) in (str, unicode, bytes):
            # remove temporary files
            for f in self.request['to_remove']:
                os.remove(f)
            return output

        # The report output gets pulled through report_frame.pt
        self.reportout = output['report_data']
        framed_output = self.frame_template()

        # this is the good part
        result = createPdf(framed_output)

        # remove temporary files
        for f in self.request['to_remove']:
            os.remove(f)

        if result:
            # Create new report object
            reportid = self.aq_parent.generateUniqueId('Report')
            report = _createObjectByType("Report", self.aq_parent, reportid)
            report.edit(Client=clientuid)
            report.processForm()

            # write pdf to report object
            report.edit(title=output['report_title'], ReportFile=result)
            report.reindexObject()

            fn = "%s - %s" % (self.date.strftime(self.date_format_short),
                              _u(output['report_title']))

            setheader = self.request.RESPONSE.setHeader
            setheader('Content-Type', 'application/pdf')
            setheader("Content-Disposition", "attachment;filename=\"%s\"" % _c(fn))
            self.request.RESPONSE.write(result)

        return


class ReferenceAnalysisQC_Samples(BrowserView):

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        # get Supplier from request
        supplier = self.request.form.get('SupplierUID', '')
        supplier = self.reference_catalog.lookupObject(supplier)
        if supplier:
            # get ReferenceSamples for this supplier
            samples = self.bika_catalog(portal_type='ReferenceSample',
                                        path={"query": "/".join(supplier.getPhysicalPath()),
                                              "level": 0})
            ret = []
            for sample in samples:
                sample = sample.getObject()
                UID = sample.UID()
                title = sample.Title()
                definition = sample.getReferenceDefinition()
                if definition:
                    title = "%s (%s)" % (title, definition.Title())
                ret.append((UID, title))
            return json.dumps(ret)


class ReferenceAnalysisQC_Services(BrowserView):

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        # get Sample from request
        sample = self.request.form.get('ReferenceSampleUID', '')
        sample = self.reference_catalog.lookupObject(sample)
        if sample:
            # get ReferenceSamples for this supplier
            analyses = self.bika_analysis_catalog(portal_type='ReferenceAnalysis',
                                                  path={"query": "/".join(sample.getPhysicalPath()),
                                                        "level": 0})
            ret = {}
            for analysis in analyses:
                service = analysis.getObject().getService()
                if service.UID() in ret:
                    ret[service.UID()]['analyses'].append(analysis.UID)
                else:
                    ret[service.UID()] = {'title': service.Title(),
                                          'analyses': [analysis.UID, ]}
            ret = [[k, v['title'], v['analyses']] for k, v in ret.items()]
            return json.dumps(ret)
