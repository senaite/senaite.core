from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from analysisrequests import QueryAnalysisRequests
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.reports.selection_macros import SelectionMacrosView
from bika.lims.interfaces import IQueries
from bika.lims.utils import logged_in_client, getUsers
from cStringIO import StringIO
from invoices import QueryInvoices
from orders import QueryOrders
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
import json
import plone
import sys

class QueryView(BrowserView):
    """ Main Query View form
    """
    implements(IViewView)
    template = ViewPageTemplateFile("queries_query.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.selection_macros = SelectionMacrosView(context, request)
        self.icon = "++resource++bika.lims.images/query_big.png"
        self.getAnalysts = getUsers(context, ['Manager', 'LabManager', 'Analyst'])

        request.set('disable_border', 1)

    def __call__(self):
        return self.template()


class SubmitForm(BrowserView):
    """ Redirect to specific query
    """
    implements(IViewView)
    template = ViewPageTemplateFile("query_frame.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

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
        self.querier = self.user_fullname(username)
        self.querier_email = self.user_email(username)
        query_id =  self.request.form['query_id']
        querytype = ''
        if query_id == 'analysisrequests':
            querytype = 'Analysis requests'
            self.queryout = QueryAnalysisRequests(self.context, self.request)()
        elif query_id == 'orders':
            querytype = 'Orders'
            self.queryout = QueryOrders(self.context, self.request)()
        elif query_id == 'invoices':
            querytype = 'Invoices'
            self.queryout = QueryInvoices(self.context, self.request)()
        else:
            self.queryout = "no query to out"


        return self.template()

