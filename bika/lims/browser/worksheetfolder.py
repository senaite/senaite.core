from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.event import ObjectEditedEvent
from Products.Archetypes.public import DisplayList
from DocumentTemplate import sequence
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims import PMF, logger
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.utils import TimeOrDate
from bika.lims.utils import getAnalysts
from plone.app.content.browser.interfaces import IFolderContentsView
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
            selected_worksheets = WorkflowAction._get_selected_items(self)
            selected_worksheet_uids = selected_worksheets.keys()

            if selected_worksheets:
                changes = False
                for uid in selected_worksheet_uids:
                    worksheet = selected_worksheets[uid]
                    # Double-check the state first
                    if workflow.getInfoFor(worksheet, 'review_state') == 'open':
                        worksheet.setAnalyst(form['Analyst'][0][uid])
                        changes = True

                if changes:
                    message = self.context.translate(PMF('Changes saved.'))
                    self.context.plone_utils.addPortalMessage(message, 'info')

            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())
            self.request.response.redirect(self.destination_url)
        else:
            # default bika_listing.py/WorkflowAction for other transitions
            WorkflowAction.__call__(self)


class WorksheetFolderListingView(BikaListingView):
    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)
        self.contentFilter = {
            'portal_type': 'Worksheet',
            'review_state':['open', 'to_be_verified', 'verified', 'rejected'],
            'sort_on':'id',
            'sort_order': 'reverse'}
        self.context_actions = {_('Add'):
                                {'url': 'worksheet_add?wsanalyst=&wstemplate=&wsinstrument=',
                                 'icon': '++resource++bika.lims.images/add.png',
                                 'class': 'worksheet_add'}}
        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = True
        self.show_select_column = True

        request.set('disable_border', 1)

        self.icon = "++resource++bika.lims.images/worksheet_big.png"
        self.title = _("Worksheets")
        self.description = _("Worksheets description", "")
        self.TimeOrDate = TimeOrDate


        pm = getToolByName(context, "portal_membership")
        bsc = getToolByName(context, 'bika_setup_catalog')

        analyst = pm.getAuthenticatedMember().getId()

        self.analysts = getAnalysts(self)

        templates = [t for t in bsc(portal_type = 'WorksheetTemplate',
                                    inactive_state = 'active')]

        self.templates = [(t.UID, t.Title) for t in templates]
        self.templates.sort(lambda x, y: cmp(x[1], y[1]))

        self.instruments = [(i.UID, i.Title) for i in \
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
            'Analyst': {'title': _('Analyst'),
                        'index':'getAnalyst'},
            'Template': {'title': _('Template'),
                         'index': 'getWorksheetTemplateTitle'},
            'Analyses': {'title': _('Analyses'),
                         'index': 'getNrAnalyses'},
            'Services': {'title': _('Services'),
                         'sortable':False},
            'SampleTypes': {'title': _('Sample Types'),
                            'sortable':False},
            'QC': {'title': _('QC'),
                   'sortable':False},
            'CreationDate': {'title': _('Creation Date'),
                             'index': 'created'},
            'state_title': {'title': _('State'),
                            'index': 'review_state'},
        }
        self.review_states = [
            {'id':'all',
             'title': _('All'),
             'contentFilter': {'portal_type': 'Worksheet',
                               'review_state':['open', 'to_be_verified', 'verified', 'rejected'],
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'transitions':['retract', 'verify', 'reject'],
             'columns':['Title',
                        'Analyst',
                        'Template',
                        'Analyses',
                        'Services',
                        'SampleTypes',
                        'QC',
                        'CreationDate',
                        'state_title']},
            {'id':'mine',
             'title': _('Mine'),
             'contentFilter': {'portal_type': 'Worksheet',
                               'review_state':['open', 'to_be_verified', 'verified', 'rejected'],
                               'getAnalyst': analyst,
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'transitions':['retract', 'verify', 'reject'],
             'columns':['Title',
                        'Analyst',
                        'Template',
                        'Analyses',
                        'Services',
                        'SampleTypes',
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
                        'Analyst',
                        'Template',
                        'Analyses',
                        'Services',
                        'SampleTypes',
                        'QC',
                        'CreationDate',
                        'state_title']},
            {'id':'to_be_verified',
             'title': _('To be verified'),
             'contentFilter': {'portal_type': 'Worksheet',
                               'review_state':'to_be_verified',
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'transitions':['retract', 'verify', 'reject'],
             'columns':['Title',
                        'Analyst',
                        'Template',
                        'Analyses',
                        'Services',
                        'SampleTypes',
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
                        'Analyst',
                        'Template',
                        'Analyses',
                        'Services',
                        'SampleTypes',
                        'QC',
                        'CreationDate',
                        'state_title']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        mtool = getToolByName(self, 'portal_membership')
        wf = getToolByName(self, 'portal_workflow')
        rc = getToolByName(self, REFERENCE_CATALOG)
        member = mtool.getAuthenticatedMember()
        new_items = []
        analyst_choices = []
        for a in self.analysts:
            analyst_choices.append({'ResultValue': a[0], 'ResultText': a[1]})
        can_reassign = False
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                new_items.append(items[x])
                continue
            obj = items[x]['obj']
            items[x]['Title'] = obj.Title()
            analyst = obj.getAnalyst().strip()
            # XXX This should not be needed - why is contentFilter/analyst not working?
            if 'getAnalyst' in self.contentFilter:
                if analyst != member.getId():
                    continue
            wst = obj.getWorksheetTemplate()
            items[x]['Template'] = wst and wst.Title() or ''
            if wst:
                items[x]['replace']['Template'] = "<a href='%s'>%s</a>" % \
                    (wst.absolute_url(), wst.Title())
            items[x]['Analyses'] = str(len(obj.getAnalyses()))
            if items[x]['Analyses'] == '0':
                # Don't display empty worksheets that aren't ours
                if member.getId() != analyst:
                    continue
                # give empties pretty classes.
                items[x]['table_row_class'] = 'state-empty-worksheet'
                items[x]['class']['Analyses'] = "empty"
            items[x]['CreationDate'] = TimeOrDate(self.context, obj.creation_date)
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
            ws_services = ws_services.values()
            ws_services.sort()
            if ws_services:
                ws_services[-1] = ws_services[-1].replace(",", "")
            items[x]['Services'] = ""
            items[x]['replace']['Services'] = " ".join(ws_services)

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

            if items[x]['review_state'] == 'open':
                items[x]['Analyst'] = analyst
                items[x]['allow_edit'] = ['Analyst', ]
                items[x]['required'] = ['Analyst', ]
                can_reassign = True
                items[x]['choices'] = {'Analyst': analyst_choices}
            else:
                analyst_member = mtool.getMemberById(analyst)
                if analyst_member != None:
                    items[x]['Analyst'] = analyst_member.getProperty('fullname')
                else:
                    items[x]['Analyst'] = ''

            new_items.append(items[x])

        if can_reassign:
            for x in range(len(self.review_states)):
                if self.review_states[x]['id'] in ['all', 'mine', 'open']:
                    self.review_states[x]['custom_actions'] = [{'id': 'reassign', 'title': 'Reassign'}, ]

        return new_items

    def getAnalysts(self):
        """ Present the LabManagers and Analysts as options for analyst
            Used in bika_listing.pt
        """
        return DisplayList(self.analysts)

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

    def __call__(self, wsanalyst = None, wstemplate = None, wsinstrument = None):
        # Validation
        if not wsanalyst:
            message = self.context.translate("Analyst must be specified.")
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.request.RESPONSE.redirect(self.context.absolute_url())
            return

        form = self.request.form
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        wf = getToolByName(self.context, "portal_workflow")
        pm = getToolByName(self.context, "portal_membership")

        _id = self.context.invokeFactory(type_name = 'Worksheet', id = 'tmp')
        ws = self.context[_id]
        ws.processForm()
        zope.event.notify(ObjectEditedEvent(ws))

        # Set analyst and instrument
        ws.setAnalyst(wsanalyst)
        if wsinstrument:
            ws.setInstrument(wsinstrument)

        # overwrite saved context UID for event subscribers
        self.request['context_uid'] = ws.UID()

        # if no template was specified, redirect to blank worksheet
        if not wstemplate:
            ws.processForm()
            self.request.RESPONSE.redirect(ws.absolute_url() + "/add_analyses")
            return

        wst = rc.lookupObject(wstemplate)
        ws.setWorksheetTemplate(wst)
        ws.applyWorksheetTemplate(wst)

        if ws.getLayout():
            self.request.RESPONSE.redirect(ws.absolute_url() + "/manage_results")
        else:
            msg = self.context.translate("No analyses were added")
            self.context.plone_utils.addPortalMessage(msg)
            self.request.RESPONSE.redirect(ws.absolute_url() + "/add_analyses")
