from analysesperservice import AnalysesPerService
from analysespersampletype import AnalysesPerSampleType
from analysesattachments import AnalysesAttachments
from analysesperclient import AnalysesPerClient
from analysestats import AnalysesTats
from analysestats_overtime import AnalysesTatsOverTime
from analysesoutofrange import AnalysesOutOfRange
from analysesrepeated import AnalysesRepeated
from arsnotinvoiced import ARsNotInvoiced
from resultspersamplepoint import ResultsPerSamplePoint
from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import TimeOrDate
from bika.lims.utils import pretty_user_name_or_id
from bika.lims.utils import pretty_user_email
from bika.lims.utils import logged_in_client
from bika.lims.utils import getUsers
from bika.lims.interfaces import IReportFolder
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
import xhtml2pdf.pisa as pisa
from zope.interface import implements
import json
import plone
from cStringIO import StringIO
import sys

class ProductivityView(BrowserView):
    """ Productivity View form
    """
    implements(IViewView)
    template = ViewPageTemplateFile("templates/reports_productivity.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.icon = "++resource++bika.lims.images/report_big.png"
        self.TimeOrDate = TimeOrDate
        self.getAnalysts = getUsers(context, ['Manager', 'LabManager', 'Analyst'])

    def __call__(self):
        return self.template()

class QualityControlView(BrowserView):
    """ QC View form
    """
    implements(IViewView)
    template = ViewPageTemplateFile("templates/reports_qualitycontrol.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.icon = "++resource++bika.lims.images/report_big.png"
        self.TimeOrDate = TimeOrDate

    def __call__(self):
        return self.template()

class AdministrationView(BrowserView):
    """ Administration View form
    """
    implements(IViewView)
    template = ViewPageTemplateFile("templates/reports_administration.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.icon = "++resource++bika.lims.images/report_big.png"
        self.TimeOrDate = TimeOrDate

    def __call__(self):
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

        self.icon = "++resource++bika.lims.images/report_big.png"
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
                'ReportType': {'title': _('Report Type')},
                'FileSize': {'title': _('Size')},
                'Created': {'title': _('Created')},
                'By': {'title': _('By')}, }
            self.review_states = [
                {'id':'default',
                 'title': 'All',
                 'contentFilter':{},
                 'columns': ['ReportType',
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
                'ReportType': {'title': _('Report Type')},
                'FileSize': {'title': _('Size')},
                'Created': {'title': _('Created')},
                'By': {'title': _('By')},
            }
            self.review_states = [
                {'id':'default',
                 'title': 'All',
                 'contentFilter':{},
                 'columns': ['Client',
                             'ReportType',
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
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
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
            items[x]['Created'] = TimeOrDate(self.context, obj.created())
            items[x]['By'] = pretty_user_name_or_id(self.context, obj.Creator())

            items[x]['replace']['ReportType'] = \
                 "<a href='%s/at_download/ReportFile'>%s</a>" % \
                 (obj_url, items[x]['ReportType'])
        return items

class SubmitForm(BrowserView):
    """ Redirect to specific report
    """
    implements(IViewView)
    template = ViewPageTemplateFile("templates/report_frame.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.TimeOrDate = TimeOrDate

    def __call__(self):
        lab = self.context.bika_setup.laboratory
        self.lab_title = lab.getName()
        self.lab_address = lab.getPrintAddress()
        self.lab_email = lab.getEmailAddress()
        self.lab_url = lab.getLabURL()
        self.date = DateTime()
        client = logged_in_client(self.context)
        if client:
            self.client_title = client.Title()
            self.client_address = client.getPrintAddress()
        else:
            self.client_title = None
            self.client_address = None

        if client:
            clientuid = client.UID()
        else:
            clientuid = None
        username = self.context.portal_membership.getAuthenticatedMember().getUserName()
        self.reporter = pretty_user_name_or_id(self.context, username)
        self.reporter_email = pretty_user_email(self.context, username)
        report_id =  self.request.form['report_id']
        reporttype = ''
        if report_id == 'analysesperservice':
            reporttype = 'Analyses per service'
            self.reportout = AnalysesPerService(self.context, self.request)()
        elif report_id == 'analysespersampletype':
            reporttype = 'Analyses per sampletype'
            self.reportout = AnalysesPerSampleType(self.context, self.request)()
        elif report_id == 'analysesperclient':
            reporttype = 'Analyses per client'
            self.reportout = AnalysesPerClient(self.context, self.request)()
        elif report_id == 'analysestats':
            reporttype = 'Analyses TATs'
            self.reportout = AnalysesTats(self.context, self.request)()
        elif report_id == 'analysestats_overtime':
            reporttype = 'Analyses TATs over time'
            self.reportout = AnalysesTatsOverTime(self.context, self.request)()
        elif report_id == 'analysesattachments':
            reporttype = 'Analyses attachments'
            self.reportout = AnalysesAttachments(self.context, self.request)()
        elif report_id == 'analysesoutofrange':
            reporttype = 'Analyses out of range'
            self.reportout = AnalysesOutOfRange(self.context, self.request)()
        elif report_id == 'analysesrepeated':
            reporttype = 'Analyses repeated'
            self.reportout = AnalysesRepeated(self.context, self.request)()
        elif report_id == 'arsnotinvoiced':
            reporttype = 'ARs not invoiced'
            self.reportout = ARsNotInvoiced(self.context, self.request)()
        elif report_id == 'resultspersamplepoint':
            reporttype = 'Results per sample point'
            self.reportout = ResultsPerSamplePoint(self.context, self.request)()
        else:
            self.reportout = "no report to out"

        # this is the good part
        ramdisk = StringIO()
        pdf = pisa.CreatePDF(self.template(), ramdisk)
        result = ramdisk.getvalue()
        ramdisk.close()

        # write pdf to report object
        reportid = self.aq_parent.generateUniqueId('Report')
        self.aq_parent.invokeFactory(id = reportid, type_name = "Report")
        report = self.aq_parent._getOb(reportid)
        report.edit(
            title = reporttype,
            ReportFile = result,
            ReportType = reporttype,
            Client = clientuid,
            )
        report.processForm()
        report.reindexObject()


        if not pdf.err:
            setheader = self.request.RESPONSE.setHeader
            setheader('Content-Type', 'application/pdf')
            self.request.RESPONSE.write(result)

        pisa.showLogging()


        return self.template()

