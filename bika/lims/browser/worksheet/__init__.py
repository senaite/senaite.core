# coding=utf-8

# Worksheet package imports
from add_analyses import AddAnalysesView
from add_blank import AddBlankView
from add_control import AddControlView
from add_duplicate import AddDuplicateView
from analyses import WorksheetAnalysesView
from analysisrequests import WorksheetARsView
from export import ExportView
from printview import WorksheetPrintView
from results import ManageResultsView
from services import WorksheetServicesView

# Regular imports
#from AccessControl import getSecurityManager
#from Products.CMFPlone.utils import _createObjectByType
#from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
#from bika.lims.permissions import EditResults, EditWorksheet, ManageWorksheets
#from bika.lims import PMF, logger
from bika.lims.browser import BrowserView
#from bika.lims.browser.analyses import AnalysesView
#from bika.lims.browser.bika_listing import BikaListingView
#from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.browser.referencesample import ReferenceSamplesView
#from bika.lims.exportimport import instruments
from bika.lims.interfaces import IFieldIcons
from bika.lims.interfaces import IWorksheet
#from bika.lims.subscribers import doActionFor
#from bika.lims.subscribers import skip
#from bika.lims.utils import to_utf8
#from bika.lims.utils import getUsers, isActive, tmpID
#from DateTime import DateTime
#from DocumentTemplate import sequence
from operator import itemgetter
#from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes.config import REFERENCE_CATALOG
#from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
#from Products.CMFCore.WorkflowCore import WorkflowException
#from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapts
from zope.component import getAdapters
#from zope.component import getMultiAdapter
from zope.interface import implements
#from bika.lims.browser.referenceanalysis import AnalysesRetractedListReport
#from DateTime import DateTime
#from Products.CMFPlone.i18nl10n import ulocalized_time
#from bika.lims.utils import to_utf8 as _c

import plone
#import plone.protect
import json




class ResultOutOfRange(object):
    """Return alerts for any analyses inside the context worksheet
    """
    implements(IFieldIcons)
    adapts(IWorksheet)

    def __init__(self, context):
        self.context = context

    def __call__(self, result=None, **kwargs):
        workflow = getToolByName(self.context, 'portal_workflow')
        items = self.context.getAnalyses()
        field_icons = {}
        for obj in items:
            obj = obj.getObject() if hasattr(obj, 'getObject') else obj
            uid = obj.UID()
            astate = workflow.getInfoFor(obj, 'review_state')
            if astate == 'retracted':
                continue
            adapters = getAdapters((obj, ), IFieldIcons)
            for name, adapter in adapters:
                alerts = adapter()
                if alerts:
                    if uid in field_icons:
                        field_icons[uid].extend(alerts[uid])
                    else:
                        field_icons[uid] = alerts[uid]
        return field_icons


def getAnalystName(context):
    """ Returns the name of the currently assigned analyst
    """
    mtool = getToolByName(context, 'portal_membership')
    analyst = context.getAnalyst().strip()
    analyst_member = mtool.getMemberById(analyst)
    if analyst_member != None:
        return analyst_member.getProperty('fullname')
    else:
        return analyst

def checkUserAccess(context, request, redirect=True):
    """ Checks if the current user has granted access to the worksheet.
        If the user is an analyst without LabManager, LabClerk and
        RegulatoryInspector roles and the option 'Allow analysts
        only to access to the Worksheets on which they are assigned' is
        ticked and the above condition is true, it will redirect to
        the main Worksheets view.
        Returns False if the user has no access, otherwise returns True
    """
    # Deny access to foreign analysts
    allowed = context.checkUserAccess()
    if allowed == False and redirect == True:
        msg =  _('You do not have sufficient privileges to view '
                 'the worksheet ${worksheet_title}.',
                 mapping={"worksheet_title": context.Title()})
        context.plone_utils.addPortalMessage(msg, 'warning')
        # Redirect to WS list
        portal = getToolByName(context, 'portal_url').getPortalObject()
        destination_url = portal.absolute_url() + "/worksheets"
        request.response.redirect(destination_url)

    return allowed

def checkUserManage(context, request, redirect=True):
    allowed = context.checkUserManage()
    if allowed == False and redirect == True:
        # Redirect to /manage_results view
        destination_url = context.absolute_url() + "/manage_results"
        request.response.redirect(destination_url)



def rejected_alerts(ws):
    if hasattr(ws, 'replaced_by'):
        uc = getToolByName(ws, 'uid_catalog')
        uid = getattr(ws, 'replaced_by')
        _ws = uc(UID=uid)[0].getObject()
        msg = _("This worksheet has been rejected.  The replacement worksheet is ${ws_id}",
                mapping={'ws_id':_ws.getId()})
        ws.plone_utils.addPortalMessage(msg)
    if hasattr(ws, 'replaces_rejected_worksheet'):
        uc = getToolByName(ws, 'uid_catalog')
        uid = getattr(ws, 'replaces_rejected_worksheet')
        _ws = uc(UID=uid)[0].getObject()
        msg = _("This worksheet has been created to replace the rejected "
                "worksheet at ${ws_id}",
                mapping={'ws_id':_ws.getId()})
        ws.plone_utils.addPortalMessage(msg)




class ajaxGetWorksheetReferences(ReferenceSamplesView):
    """ Display reference samples matching services in this worksheet
        add_blank and add_control use this to refresh the list of reference
        samples when service checkboxes are selected
    """
    implements(IViewView)

    def __init__(self, context, request):
        super(ajaxGetWorksheetReferences, self).__init__(context, request)
        self.catalog = 'bika_catalog'
        self.contentFilter = {'portal_type': 'ReferenceSample'}
        self.context_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = False
        self.show_workflow_action_buttons = False
        self.pagesize = 50
        # must set service_uids in __call__ before delegating to super
        self.service_uids = []
        # must set control_type='b' or 'c' in __call__ before delegating
        self.control_type = ""
        self.columns['Services'] = {'title': _('Services')}
        self.columns['Definition'] = {'title': _('Reference Definition')}
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{'review_state':'current'},
             'columns': ['ID',
                         'Title',
                         'Definition',
                         'ExpiryDate',
                         'Services']
             },
        ]

    def folderitems(self):
        translate = self.context.translate
        workflow = getToolByName(self.context, 'portal_workflow')
        items = super(ajaxGetWorksheetReferences, self).folderitems()
        new_items = []
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            if self.control_type == 'b' and not obj.getBlank(): continue
            if self.control_type == 'c' and obj.getBlank(): continue
            ref_services = obj.getServices()
            ws_ref_services = [rs for rs in ref_services if
                               rs.UID() in self.service_uids]
            if ws_ref_services:
                if workflow.getInfoFor(obj, 'review_state') != 'current':
                    continue
                services = [rs.Title() for rs in ws_ref_services]
                items[x]['nr_services'] = len(services)
                items[x]['Definition'] = (obj.getReferenceDefinition() and obj.getReferenceDefinition().Title()) or ''
                services.sort(lambda x, y: cmp(x.lower(), y.lower()))
                items[x]['Services'] = ", ".join(services)
                items[x]['replace'] = {}

                after_icons = "<a href='%s' target='_blank'><img src='++resource++bika.lims.images/referencesample.png' title='%s: %s'></a>" % \
                    (obj.absolute_url(), \
                     t(_("Reference sample")), obj.Title())
                items[x]['before']['ID'] = after_icons

                new_items.append(items[x])

        new_items = sorted(new_items, key = itemgetter('nr_services'))
        new_items.reverse()

        return new_items

    def __call__(self):
        self.service_uids = self.request.get('service_uids', '').split(",")
        self.control_type = self.request.get('control_type', '')
        if not self.control_type:
            return t(_("No control type specified"))
        return super(ajaxGetWorksheetReferences, self).contents_table()


class ajaxGetServices(BrowserView):
    """ When a Category is selected in the add_analyses search screen, this
        function returns a list of services from the selected category.
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        return json.dumps([c.Title for c in
                bsc(portal_type = 'AnalysisService',
                   getCategoryTitle = self.request.get('getCategoryTitle', ''),
                   inactive_state = 'active',
                   sort_on = 'sortable_title')])

class ajaxAttachAnalyses(BrowserView):
    """ In attachment add form,
        the analyses dropdown combo uses this as source.
        Form is handled by the worksheet ManageResults code
    """
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


class ajaxSetAnalyst():
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

class ajaxSetInstrument():
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
