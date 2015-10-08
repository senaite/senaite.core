# coding=utf-8
from AccessControl import getSecurityManager
from DateTime import DateTime
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.i18nl10n import ulocalized_time
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements

from bika.lims import bikaMessageFactory as _
from bika.lims import EditResults, EditWorksheet, ManageWorksheets
from bika.lims import PMF, logger
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.worksheet.tools import checkUserManage
from bika.lims.browser.worksheet.tools import showRejectionMessage
from bika.lims.utils import t


class AddAnalysesView(BikaListingView):
    implements(IViewView)
    template = ViewPageTemplateFile("../templates/add_analyses.pt")

    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)
        self.icon = self.portal_url + "/++resource++bika.lims.images/worksheet_big.png"
        self.title = self.context.translate(_("Add Analyses"))
        self.description = ""
        self.catalog = "bika_analysis_catalog"
        self.context_actions = {}
        # initial review state for first form display of the worksheet
        # add_analyses search view - first batch of analyses, latest first.
        self.contentFilter = {'portal_type': 'Analysis',
                              'review_state':'sample_received',
                              'worksheetanalysis_review_state':'unassigned',
                              'cancellation_state':'active'}
        self.base_url = self.context.absolute_url()
        self.view_url = self.base_url + "/add_analyses"
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50

        self.columns = {
            'Client': {
                'title': _('Client'),
                'index':'getClientTitle'},
            'getClientOrderNumber': {
                'title': _('Order'),
                'index': 'getClientOrderNumber'},
            'getRequestID': {
                'title': _('Request ID'),
                'index': 'getRequestID'},
            'Priority': {
                'title': _('Priority'),
                'index': 'Priority'},
            'CategoryTitle': {
                'title': _('Category'),
                'index':'getCategoryTitle'},
            'Title': {
                'title': _('Analysis'),
                'index':'sortable_title'},
            'getDateReceived': {
                'title': _('Date Received'),
                'index': 'getDateReceived'},
            'getDueDate': {
                'title': _('Due Date'),
                'index': 'getDueDate'},
        }
        self.filter_indexes = ['Title',]
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter': {},
             'transitions': [{'id':'assign'}, ],
             'columns':['Client',
                        'getClientOrderNumber',
                        'getRequestID',
                        'Priority',
                        'CategoryTitle',
                        'Title',
                        'getDateReceived',
                        'getDueDate'],
            },
        ]

    def __call__(self):
        if not(getSecurityManager().checkPermission(EditWorksheet, self.context)):
            self.request.response.redirect(self.context.absolute_url())
            return

        # Deny access to foreign analysts
        if checkUserManage(self.context, self.request) == False:
            return []

        showRejectionMessage(self.context)

        translate = self.context.translate

        form_id = self.form_id
        form = self.request.form
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        if 'submitted' in form:
            if 'getWorksheetTemplate' in form and form['getWorksheetTemplate']:
                layout = self.context.getLayout()
                wst = rc.lookupObject(form['getWorksheetTemplate'])
                self.request['context_uid'] = self.context.UID()
                self.context.applyWorksheetTemplate(wst)
                if len(self.context.getLayout()) != len(layout):
                    self.context.plone_utils.addPortalMessage(
                        PMF("Changes saved."))
                    self.request.RESPONSE.redirect(self.context.absolute_url() +
                                                   "/manage_results")
                else:
                    self.context.plone_utils.addPortalMessage(
                        _("No analyses were added to this worksheet."))
                    self.request.RESPONSE.redirect(self.context.absolute_url() +
                                                   "/add_analyses")

        self._process_request()

        if self.request.get('table_only', '') == self.form_id:
            return self.contents_table()
        else:
            return self.template()

    def folderitems(self):

        items = BikaListingView.folderitems(self)
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        roles = member.getRoles()
        hideclientlink = 'RegulatoryInspector' in roles \
            and 'Manager' not in roles \
            and 'LabManager' not in roles \
            and 'LabClerk' not in roles

        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            service = obj.getService()
            client = obj.aq_parent.aq_parent
            items[x]['getClientOrderNumber'] = obj.getClientOrderNumber()
            items[x]['getDateReceived'] = self.ulocalized_time(obj.getDateReceived())
            DueDate = obj.getDueDate()
            items[x]['getDueDate'] = self.ulocalized_time(DueDate)
            if DueDate < DateTime():
                items[x]['after']['DueDate'] = '<img width="16" height="16" src="%s/++resource++bika.lims.images/late.png" title="%s"/>' % \
                    (self.context.absolute_url(),
                     t(_("Late Analysis")))
            items[x]['CategoryTitle'] = service.getCategory() and service.getCategory().Title() or ''

            if getSecurityManager().checkPermission(EditResults, obj.aq_parent):
                url = obj.aq_parent.absolute_url() + "/manage_results"
            else:
                url = obj.aq_parent.absolute_url()
            items[x]['getRequestID'] = obj.aq_parent.getRequestID()
            items[x]['replace']['getRequestID'] = "<a href='%s'>%s</a>" % \
                 (url, items[x]['getRequestID'])
            items[x]['Priority'] = ''


            items[x]['Client'] = client.Title()
            if hideclientlink == False:
                items[x]['replace']['Client'] = "<a href='%s'>%s</a>" % \
                    (client.absolute_url(), client.Title())

        return items

    def getServices(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        return [c.Title for c in
                bsc(portal_type = 'AnalysisService',
                   getCategoryUID = self.request.get('list_getCategoryUID', ''),
                   inactive_state = 'active',
                   sort_on = 'sortable_title')]

    def getClients(self):
        pc = getToolByName(self.context, 'portal_catalog')
        return [c.Title for c in
                pc(portal_type = 'Client',
                   inactive_state = 'active',
                   sort_on = 'sortable_title')]

    def getCategories(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        return [c.Title for c in
                bsc(portal_type = 'AnalysisCategory',
                   inactive_state = 'active',
                   sort_on = 'sortable_title')]

    def getWorksheetTemplates(self):
        """ Return WS Templates """
        profiles = []
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        return [(c.UID, c.Title) for c in
                bsc(portal_type = 'WorksheetTemplate',
                   inactive_state = 'active',
                   sort_on = 'sortable_title')]
