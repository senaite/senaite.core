from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import DisplayList
from DocumentTemplate import sequence
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims import PMF, logger
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.permissions import EditWorksheet
from bika.lims.permissions import ManageWorksheets
from bika.lims.utils import getUsers, tmpID
from bika.lims.utils import to_utf8 as _c
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
import plone
import json
import zope

class WorksheetFolderWorkflowAction(WorkflowAction):
    """ Workflow actions taken in the WorksheetFolder
        This function is called to do the workflow actions
        that apply to worksheets in the WorksheetFolder
    """
    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(form)
        workflow = getToolByName(self.context, 'portal_workflow')
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        action, came_from = WorkflowAction._get_form_workflow_action(self)

        if action == 'reassign':
            mtool = getToolByName(self.context, 'portal_membership')
            if not mtool.checkPermission(ManageWorksheets, self.context):

                # Redirect to WS list
                msg = _('You do not have sufficient privileges to '
                        'manage worksheets.')
                self.context.plone_utils.addPortalMessage(msg, 'warning')
                portal = getToolByName(self.context, 'portal_url').getPortalObject()
                self.destination_url = portal.absolute_url() + "/worksheets"
                self.request.response.redirect(self.destination_url)
                return

            selected_worksheets = WorkflowAction._get_selected_items(self)
            selected_worksheet_uids = selected_worksheets.keys()

            if selected_worksheets:
                changes = False
                for uid in selected_worksheet_uids:
                    worksheet = selected_worksheets[uid]
                    # Double-check the state first
                    if workflow.getInfoFor(worksheet, 'review_state') == 'open':
                        worksheet.setAnalyst(form['Analyst'][0][uid])
                        worksheet.reindexObject(idxs=['getAnalyst'])
                        changes = True

                if changes:
                    message = PMF('Changes saved.')
                    self.context.plone_utils.addPortalMessage(message, 'info')

            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())
            self.request.response.redirect(self.destination_url)
        else:
            # default bika_listing.py/WorkflowAction for other transitions
            WorkflowAction.__call__(self)


class WorksheetFolderListingView(BikaListingView):

    implements(IFolderContentsView, IViewView)

    template = ViewPageTemplateFile("templates/worksheetfolder.pt")

    def __init__(self, context, request):
        super(WorksheetFolderListingView, self).__init__(context, request)
        self.catalog = 'bika_catalog'
        self.contentFilter = {
            'portal_type': 'Worksheet',
            'review_state':['open', 'to_be_verified', 'verified'],
            'sort_on':'id',
            'sort_order': 'reverse'}
        self.context_actions = {_('Add'):
                                {'url': 'worksheet_add',
                                 'icon': '++resource++bika.lims.images/add.png',
                                 'class': 'worksheet_add'}}
        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = True
        self.show_select_column = True
        self.pagesize = 25
        self.restrict_results = False

        request.set('disable_border', 1)

        self.icon = self.portal_url + "/++resource++bika.lims.images/worksheet_big.png"
        self.title = _("Worksheets")
        self.description = ""

        pm = getToolByName(context, "portal_membership")
        # this is a property of self, because self.getAnalysts returns it
        self.analysts = getUsers(self, ['Manager', 'LabManager', 'Analyst'])
        self.analysts = self.analysts.sortedByKey()

        bsc = getToolByName(context, 'bika_setup_catalog')
        templates = [t for t in bsc(portal_type = 'WorksheetTemplate',
                                    inactive_state = 'active')]

        self.templates = [(t.UID, t.Title) for t in templates]
        self.templates.sort(lambda x, y: cmp(x[1], y[1]))

        self.instruments = [(i.UID, i.Title) for i in
                            bsc(portal_type = 'Instrument',
                                inactive_state = 'active')]
        self.instruments.sort(lambda x, y: cmp(x[1], y[1]))

        self.templateinstruments = {}
        for t in templates:
            i = t.getObject().getInstrument()
            if i:
                self.templateinstruments[t.UID] = i.UID()
            else:
                self.templateinstruments[t.UID] = ''

        self.columns = {
            'Title': {'title': _('Worksheet'),
                      'index': 'sortable_title'},
            'getPriority': {
                'title': _('Priority'),
                'index': 'getPriority'},
            'Analyst': {'title': _('Analyst'),
                        'index':'getAnalyst',
                        'toggle': True},
            'Template': {'title': _('Template'),
                         'toggle': True},
            'Services': {'title': _('Services'),
                         'sortable':False,
                         'toggle': False},
            'SampleTypes': {'title': _('Sample Types'),
                            'sortable':False,
                            'toggle': False},
            'Instrument': {'title': _('Instrument'),
                            'sortable':False,
                            'toggle': False},
            'QC': {'title': _('QC'),
                   'sortable':False,
                   'toggle': False},
            'CreationDate': {'title': PMF('Date Created'),
                             'toggle': True,
                             'index': 'created'},
            'state_title': {'title': _('State'),
                            'index': 'review_state'},
        }
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter': {'portal_type': 'Worksheet',
                               'review_state':['open', 'to_be_verified', 'verified'],
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'transitions':[{'id':'retract'},
                            {'id':'verify'},
                            {'id':'reject'}],
             'columns':['Title',
                        'getPriority',
                        'Analyst',
                        'Template',
                        'Services',
                        'SampleTypes',
                        'Instrument',
                        'QC',
                        'CreationDate',
                        'state_title']},
            # getAuthenticatedMember does not work in __init__
            # so 'mine' is configured further in 'folderitems' below.
            {'id':'mine',
             'title': _('Mine'),
             'contentFilter': {'portal_type': 'Worksheet',
                               'review_state':['open', 'to_be_verified', 'verified'],
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'transitions':[{'id':'retract'},
                            {'id':'verify'},
                            {'id':'reject'}],
             'columns':['Title',
                        'getPriority',
                        'Analyst',
                        'Template',
                        'Services',
                        'SampleTypes',
                        'Instrument',
                        'QC',
                        'CreationDate',
                        'state_title']},
            {'id':'open',
             'title': _('Open'),
             'contentFilter': {'portal_type': 'Worksheet',
                               'review_state':'open',
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'transitions':[],
             'columns':['Title',
                        'getPriority',
                        'Analyst',
                        'Template',
                        'Services',
                        'SampleTypes',
                        'Instrument',
                        'QC',
                        'CreationDate',
                        'state_title']},
            {'id':'to_be_verified',
             'title': _('To be verified'),
             'contentFilter': {'portal_type': 'Worksheet',
                               'review_state':'to_be_verified',
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'transitions':[{'id':'retract'},
                            {'id':'verify'},
                            {'id':'reject'}],
             'columns':['Title',
                        'getPriority',
                        'Analyst',
                        'Template',
                        'Services',
                        'SampleTypes',
                        'Instrument',
                        'QC',
                        'CreationDate',
                        'state_title']},
            {'id':'verified',
             'title': _('Verified'),
             'contentFilter': {'portal_type': 'Worksheet',
                               'review_state':'verified',
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'transitions':[],
             'columns':['Title',
                        'getPriority',
                        'Analyst',
                        'Template',
                        'Services',
                        'SampleTypes',
                        'Instrument',
                        'QC',
                        'CreationDate',
                        'state_title']},
        ]

    def __call__(self):
        if not self.isManagementAllowed():
            # The current has no prvileges to manage WS.
            # Remove the add button
            self.context_actions = {}

        return super(WorksheetFolderListingView, self).__call__()

    def isManagementAllowed(self):
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.checkPermission(ManageWorksheets, self.context)

    def isEditionAllowed(self):
        pm = getToolByName(self.context, "portal_membership")
        checkPermission = self.context.portal_membership.checkPermission
        return checkPermission(EditWorksheet, self.context)

    def isItemAllowed(self, obj):
        # Only show "my" worksheets
        # this cannot be setup in contentFilter,
        # because AuthenticatedMember is not available in __init__
        if self.selected_state == 'mine' or self.restrict_results == True:
            analyst = obj.getAnalyst().strip()
            if analyst != _c(self.member.getId()):
                return False

        return BikaListingView.isItemAllowed(self, obj)

    def folderitems(self):
        wf = getToolByName(self, 'portal_workflow')
        rc = getToolByName(self, REFERENCE_CATALOG)
        pm = getToolByName(self.context, "portal_membership")

        self.member = pm.getAuthenticatedMember()
        roles = self.member.getRoles()
        self.restrict_results = 'Manager' not in roles \
                and 'LabManager' not in roles \
                and 'LabClerk' not in roles \
                and 'RegulatoryInspector' not in roles \
                and self.context.bika_setup.getRestrictWorksheetUsersAccess()

        if self.restrict_results == True:
            # Remove 'Mine' button and hide 'Analyst' column
            del self.review_states[1] # Mine
            self.columns['Analyst']['toggle'] = False

        can_manage = pm.checkPermission(ManageWorksheets, self.context)

        self.selected_state = self.request.get("%s_review_state"%self.form_id,
                                                'default')

        items = BikaListingView.folderitems(self)
        new_items = []
        analyst_choices = []
        for a in self.analysts:
            analyst_choices.append({'ResultValue': a,
                                    'ResultText': self.analysts.getValue(a)})
        can_reassign = False
        self.allow_edit = self.isEditionAllowed()

        for x in range(len(items)):
            if not items[x].has_key('obj'):
                new_items.append(items[x])
                continue

            obj = items[x]['obj']

            analyst = obj.getAnalyst().strip()
            creator = obj.Creator().strip()
            items[x]['Analyst'] = analyst

            instrument = obj.getInstrument()
            items[x]['Instrument'] = instrument and instrument.Title() or ''

            items[x]['Title'] = obj.Title()
            wst = obj.getWorksheetTemplate()
            items[x]['Template'] = wst and wst.Title() or ''
            if wst:
                items[x]['replace']['Template'] = "<a href='%s'>%s</a>" % \
                    (wst.absolute_url(), wst.Title())

            items[x]['getPriority'] = ''
            items[x]['CreationDate'] = self.ulocalized_time(obj.creation_date)

            nr_analyses = len(obj.getAnalyses())
            if nr_analyses == '0':
                # give empties pretty classes.
                items[x]['table_row_class'] = 'state-empty-worksheet'

            layout = obj.getLayout()

            if len(layout) > 0:
                items[x]['replace']['Title'] = "<a href='%s/manage_results'>%s</a>" % \
                    (items[x]['url'], items[x]['Title'])
            else:
                items[x]['replace']['Title'] = "<a href='%s/add_analyses'>%s</a>" % \
                    (items[x]['url'], items[x]['Title'])

            # set Services
            ws_services = {}
            for slot in [s for s in layout if s['type'] == 'a']:
                analysis = rc.lookupObject(slot['analysis_uid'])
                service = analysis.getService()
                title = service.Title()
                if title not in ws_services:
                    ws_services[title] = "<a href='%s'>%s,</a>" % \
                        (service.absolute_url(), title)
            keys = list(ws_services.keys())
            keys.sort()
            services = []
            for key in keys:
                services.append(ws_services[key])
            if services:
                services[-1] = services[-1].replace(",", "")
            items[x]['Services'] = ""
            items[x]['replace']['Services'] = " ".join(services)

            # set Sample Types
            pos_parent = {}
            for slot in layout:
                if slot['position'] in pos_parent:
                    continue
                pos_parent[slot['position']] = rc.lookupObject(slot['container_uid'])

            sampletypes = {}
            blanks = {}
            controls = {}
            for container in pos_parent.values():
                if container.portal_type == 'AnalysisRequest':
                    sampletypes["<a href='%s'>%s,</a>" % \
                               (container.getSample().getSampleType().absolute_url(),
                                container.getSample().getSampleType().Title())] = 1
                if container.portal_type == 'ReferenceSample' and container.getBlank():
                    blanks["<a href='%s'>%s,</a>" % \
                           (container.absolute_url(),
                            container.Title())] = 1
                if container.portal_type == 'ReferenceSample' and not container.getBlank():
                    controls["<a href='%s'>%s,</a>" % \
                           (container.absolute_url(),
                            container.Title())] = 1
            sampletypes = list(sampletypes.keys())
            sampletypes.sort()
            blanks = list(blanks.keys())
            blanks.sort()
            controls = list(controls.keys())
            controls.sort()

            # remove trailing commas
            if sampletypes:
                sampletypes[-1] = sampletypes[-1].replace(",", "")
            if controls:
                controls[-1] = controls[-1].replace(",", "")
            else:
                if blanks:
                    blanks[-1] = blanks[-1].replace(",", "")

            items[x]['SampleTypes'] = ""
            items[x]['replace']['SampleTypes'] = " ".join(sampletypes)
            items[x]['QC'] = ""
            items[x]['replace']['QC'] = " ".join(blanks + controls)

            if items[x]['review_state'] == 'open' \
                and self.allow_edit \
                and self.restrict_results == False \
                and can_manage == True:
                items[x]['allow_edit'] = ['Analyst', ]
                items[x]['required'] = ['Analyst', ]
                can_reassign = True
                items[x]['choices'] = {'Analyst': analyst_choices}

            new_items.append(items[x])

        if can_reassign:
            for x in range(len(self.review_states)):
                if self.review_states[x]['id'] in ['default', 'mine', 'open']:
                    self.review_states[x]['custom_actions'] = [{'id': 'reassign', 'title': _('Reassign')}, ]

        self.show_select_column = can_reassign
        self.show_workflow_action_buttons = can_reassign

        return new_items

    def getAnalysts(self):
        """ Present the LabManagers and Analysts as options for analyst
            Used in bika_listing.pt
        """
        return self.analysts

    def getWorksheetTemplates(self):
        """ List of templates
            Used in bika_listing.pt
        """
        return DisplayList(self.templates)

    def getInstruments(self):
        """ List of instruments
            Used in bika_listing.pt
        """
        return DisplayList(self.instruments)

    def getTemplateInstruments(self):
        """ Distionary of instruments per template
            Used in bika_listing.pt
        """
        return json.dumps(self.templateinstruments)


class AddWorksheetView(BrowserView):
    """ Handler for the "Add Worksheet" button in Worksheet Folder.
        If a template was selected, the worksheet is pre-populated here.
    """

    def __call__(self):

        # Validation
        form = self.request.form
        analyst = self.request.get('analyst', '')
        template = self.request.get('template', '')
        instrument = self.request.get('instrument', '')

        if not analyst:
            message = _("Analyst must be specified.")
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.request.RESPONSE.redirect(self.context.absolute_url())
            return

        rc = getToolByName(self.context, REFERENCE_CATALOG)
        wf = getToolByName(self.context, "portal_workflow")
        pm = getToolByName(self.context, "portal_membership")

        ws = _createObjectByType("Worksheet", self.context, tmpID())
        ws.processForm()

        # Set analyst and instrument
        ws.setAnalyst(analyst)
        if instrument:
            ws.setInstrument(instrument)

        # overwrite saved context UID for event subscribers
        self.request['context_uid'] = ws.UID()

        # if no template was specified, redirect to blank worksheet
        if not template:
            ws.processForm()
            self.request.RESPONSE.redirect(ws.absolute_url() + "/add_analyses")
            return

        wst = rc.lookupObject(template)
        ws.setWorksheetTemplate(wst)
        ws.applyWorksheetTemplate(wst)

        if ws.getLayout():
            self.request.RESPONSE.redirect(ws.absolute_url() + "/manage_results")
        else:
            msg = _("No analyses were added")
            self.context.plone_utils.addPortalMessage(msg)
            self.request.RESPONSE.redirect(ws.absolute_url() + "/add_analyses")
