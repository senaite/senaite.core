# coding=utf-8
from AccessControl import getSecurityManager
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements

from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.permissions import EditWorksheet
from bika.lims.browser import BrowserView
from bika.lims.browser.worksheet.tools import checkUserManage
from bika.lims.browser.worksheet.tools import showRejectionMessage
from bika.lims.browser.worksheet.views.services import ServicesView


class AddBlankView(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("../templates/add_control.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.icon = self.portal_url + "/++resource++bika.lims.images/worksheet_big.png"
        self.title = self.context.translate(_("Add Blank Reference"))
        self.description = self.context.translate(_(
                             "Select services in the left column to locate "
                             "reference samples. Select a reference by clicking it. "))

    def __call__(self):
        if not(getSecurityManager().checkPermission(EditWorksheet, self.context)):
            self.request.response.redirect(self.context.absolute_url())
            return

        # Deny access to foreign analysts
        if checkUserManage(self.context, self.request) == False:
            return []

        showRejectionMessage(self.context)

        form = self.request.form
        if 'submitted' in form:
            rc = getToolByName(self.context, REFERENCE_CATALOG)
            # parse request
            service_uids = form['selected_service_uids'].split(",")
            position = form['position']
            reference_uid = form['reference_uid']
            reference = rc.lookupObject(reference_uid)
            self.request['context_uid'] = self.context.UID()
            ref_analyses = self.context.addReferences(position, reference, service_uids)
            self.request.response.redirect(self.context.absolute_url() + "/manage_results")
        else:
            self.Services = ServicesView(self.context, self.request)
            self.Services.view_url = self.Services.base_url + "/add_blank"
            return self.template()

    def getAvailablePositions(self):
        """ Return a list of empty slot numbers
        """
        layout = self.context.getLayout()
        used_positions = [int(slot['position']) for slot in layout]
        if used_positions:
            available_positions = [pos for pos in range(1, max(used_positions) + 1) if
                                   pos not in used_positions]
        else:
            available_positions = []
        return available_positions

    def getPriorityIcon(self):
        priority = self.context.getPriority()
        if priority:
            icon = priority.getBigIcon()
            if icon:
                return '/'.join(icon.getPhysicalPath())
