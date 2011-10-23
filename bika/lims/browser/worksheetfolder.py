from DateTime import DateTime
from DocumentTemplate import sequence
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import TimeOrDate
from bika.lims.browser.worksheet import getAnalysts
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.interface import implements
import plone

class WorksheetFolderListingView(BikaListingView):
    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)
        self.contentFilter = {
            'portal_type': 'Worksheet',
            'review_state':['open', 'to_be_verified', 'verified', 'rejected'],
            'sort_on':'id',
            'sort_order': 'reverse'}
        self.content_add_actions = {_('Worksheet'): "worksheet_add"}
        self.show_editable_border = False
        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = True
        self.show_select_column = True
        self.pagesize = 50

        self.icon = "++resource++bika.lims.images/worksheet_big.png"
        self.title = "%s: %s" % (self.context.Title(), _("Worksheets"))
        self.description = ""
        self.TimeOrDate = TimeOrDate

        pm = getToolByName(context, "portal_membership")
        analyst = pm.getAuthenticatedMember().getId()

        self.columns = {
            'Title': {'title': _('Worksheet Number')},
            'Owner': {'title': _('Owner')},
            'Analyst': {'title': _('Analyst')},
            'Template': {'title': _('Template')},
            'Analyses': {'title': _('Analyses')},
            'Services': {'title': _('Services')},
            'SampleTypes': {'title': _('Sample Types')},
            'QC': {'title': _('QC')},
            'CreationDate': {'title': _('Creation Date')},
            'state_title': {'title': _('State')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'contentFilter': {'portal_type': 'Worksheet',
                               'review_state':['open', 'to_be_verified', 'verified', 'rejected'],
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'transitions':[],
             'columns':['Title',
                        'Owner',
                        'Analyst',
                        'Template',
                        'Analyses',
                        'Services',
                        'SampleTypes',
                        'QC',
                        'CreationDate',
                        'state_title']},
            {'title': _('Mine'), 'id':'mine',
             'contentFilter': {'portal_type': 'Worksheet',
                               'review_state':['open', 'to_be_verified', 'verified', 'rejected'],
                               'getAnalyst': analyst,
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'transitions':[],
             'columns':['Title',
                        'Owner',
                        'Analyst',
                        'Template',
                        'Analyses',
                        'Services',
                        'SampleTypes',
                        'QC',
                        'CreationDate',
                        'state_title']},
            {'title': _('Worksheet Open'), 'id':'open',
             'contentFilter': {'portal_type': 'Worksheet',
                               'review_state':'open',
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'transitions':[],
             'columns':['Title',
                        'Owner',
                        'Analyst',
                        'Template',
                        'Analyses',
                        'Services',
                        'SampleTypes',
                        'QC',
                        'CreationDate',
                        'state_title']},
            {'title': _('To Be Verified'), 'id':'to_be_verified',
             'contentFilter': {'portal_type': 'Worksheet',
                               'review_state':'to_be_verified',
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'transitions':[],
             'columns':['Title',
                        'Owner',
                        'Analyst',
                        'Template',
                        'Analyses',
                        'Services',
                        'SampleTypes',
                        'QC',
                        'CreationDate',
                        'state_title']},
            {'title': _('Verified'), 'id':'verified',
             'contentFilter': {'portal_type': 'Worksheet',
                               'review_state':'verified',
                               'sort_on':'id',
                               'sort_order': 'reverse'},
             'transitions':[],
             'columns':['Title',
                        'Owner',
                        'Analyst',
                        'Template',
                        'Analyses',
                        'Services',
                        'SampleTypes',
                        'QC',
                        'CreationDate',
                        'state_title']},
##                {'title': _('Cancelled'), 'id':'cancelled',
##                 'contentFilter': {'portal_type': 'Worksheet',
##                                   'cancellation_state':'cancelled',
##                                   'sort_on':'id',
##                                   'sort_order': 'reverse'},
##                 'transitions':[],
##                 'columns':['Title',
##                            'Owner',
##                            'Analyst',
##                            'Template',
##                            'Analyses',
##                            'CreationDate',
##                            'state_title']},
# XXX reject workflow - one transition, to set a flag
# "has been rejected in the past" on this worksheet.
##                {'title': _('Rejected'), 'id':'rejected',
##                 'contentFilter': {'review_state':'open'},
##                 'columns':['Title',
##                            'Owner',
##                            'Analyst',
##                            'Template',
##                            'Analyses',
##                            'SampleTypes',
##                            'CreationDate',
##                            'state_title']}
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        mtool = getToolByName(self, 'portal_membership')
        wf = getToolByName(self, 'portal_workflow')
        rc = getToolByName(self, 'reference_catalog')
        member = mtool.getAuthenticatedMember()
        new_items = []
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                new_items.append(items[x])
                continue
            obj = items[x]['obj']
            items[x]['Title'] = obj.Title()
            items[x]['Owner'] = obj.getOwnerTuple()[1]
            analyst = obj.getAnalyst().strip()
            analyst_member = mtool.getMemberById(analyst)
            # XXX This should not be needed - why is contentFilter/analyst not working?
            if 'getAnalyst' in self.contentFilter:
                if analyst != member.getId():
                    continue
            if analyst_member != None:
                items[x]['Analyst'] = analyst_member.getProperty('fullname')
            else:
                items[x]['Analyst'] = ''
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
                    ws_services[title] = "<a href='%s'>%s</a>" % \
                        (service.absolute_url(), title)
            ws_services = ws_services.values()
            ws_services.sort()
            items[x]['Services'] = ""
            items[x]['replace']['Services'] = ", ".join(ws_services)

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
                    sampletypes["<a href='%s'>%s</a>" % \
                               (container.getSample().getSampleType().absolute_url(),
                                container.getSample().getSampleType().Title())] = 1
                if container.portal_type == 'ReferenceSample' and container.getBlank():
                    blanks["<a href='%s'>%s</a>" % \
                           (container.absolute_url(),
                            container.Title())] = 1
                if container.portal_type == 'ReferenceSample' and not container.getBlank():
                    controls["<a href='%s'>%s</a>" % \
                           (container.absolute_url(),
                            container.Title())] = 1
            sampletypes = list(sampletypes.keys())
            sampletypes.sort()
            blanks = list(blanks.keys())
            blanks.sort()
            controls = list(controls.keys())
            controls.sort()
            items[x]['SampleTypes'] = ""
            items[x]['replace']['SampleTypes'] = ", ".join(sampletypes)
            items[x]['QC'] = ""
            items[x]['replace']['QC'] = ", ".join(blanks + controls)

            new_items.append(items[x])
        return new_items

class AddWorksheetView(BrowserView):
    """ Handler for the "Add Worksheet" button in Worksheet Folder.
        If a template was selected, the worksheet is pre-populated here.
    """

    def __call__(self):
        form = self.request.form
        rc = getToolByName(self.context, "reference_catalog")
        pc = getToolByName(self.context, "portal_catalog")
        wf = getToolByName(self.context, "portal_workflow")
        pm = getToolByName(self.context, "portal_membership")

        ws_id = self.context.generateUniqueId('Worksheet')
        self.context.invokeFactory(id = ws_id, type_name = 'Worksheet')
        ws = self.context[ws_id]
        ws.processForm()

        # Current member as analyst
        member_id = pm.getAuthenticatedMember().getId()
        if member_id in [m[0] for m in getAnalysts(self.context)]:
            ws.setAnalyst(member_id)

        # overwrite saved context UID for event subscribers
        self.request['context_uid'] = ws.UID()

        # if no template was specified, redirect to blank worksheet
        if not form.has_key('wstemplate') or not form['wstemplate']:
            ws.processForm()
            self.request.RESPONSE.redirect(ws.absolute_url() + "/add_analyses")
            return

        wst = rc.lookupObject(form['wstemplate'])
        wstlayout = wst.getLayout()
        services = wst.getService()
        wst_service_uids = [s.UID() for s in services]
        ws.setWorksheetTemplate(wst)

        analyses = pc(portal_type = 'Analysis',
                      getServiceUID = wst_service_uids,
                      review_state = 'sample_received',
                      worksheetanalysis_review_state = 'unassigned',
                      sort_on = 'getDueDate')
        # collect analyses from the first X ARs.
        ar_analyses = {} # ar_uid : [analyses]
        ars = [] # for sorting
        wst_positions = len([row for row in wstlayout if row['type'] == 'a'])
        for analysis in analyses:
            ar = analysis.getRequestID
            if ar in ar_analyses:
                ar_analyses[ar].append(analysis.getObject())
            else:
                if len(ar_analyses.keys()) < wst_positions:
                    ars.append(ar)
                    ar_analyses[ar] = [analysis.getObject(), ]

        positions = [row['pos'] for row in wstlayout if row['type'] == 'a']
        for ar in ars:
            for analysis in ar_analyses[ar]:
                ws.addAnalysis(analysis, position=positions[ars.index(ar)])
                wf.doActionFor(analysis, 'assign')

        # find best maching reference samples for Blanks and Controls
        for t in ('b', 'c'):
            form_key = t == 'b' and 'blank_ref' or 'control_ref'
            for row in [r for r in wstlayout if r['type'] == t]:
                reference_definition_uid = row[form_key]
                reference_definition = rc.lookupObject(reference_definition_uid)
                samples = pc(portal_type = 'ReferenceSample',
                             review_state = 'current',
                             inactive_state = 'active',
                             getReferenceDefinitionUID = reference_definition_uid)
                if not samples:
                    msg = self.context.translate(
                        "message_no_references_found",
                        mapping = {'position':row['pos'],
                                   'definition':reference_definition.Title() and \
                                   reference_definition.Title() or ''},
                        default = "No reference samples found for " + \
                        "${definition} at position ${position}.",
                        domain = "bika.lims")
                    self.context.plone_utils.addPortalMessage(msg)
                    break
                samples = [s.getObject() for s in samples]
                if t == 'b':
                    samples = [s for s in samples if s.getBlank()]
                else:
                    samples = [s for s in samples if not s.getBlank()]
                complete_reference_found = False
                references = {}
                for reference in samples:
                    reference_uid = reference.UID()
                    references[reference_uid] = {}
                    references[reference_uid]['services'] = []
                    references[reference_uid]['count'] = 0
                    specs = reference.getResultsRangeDict()
                    for service_uid in wst_service_uids:
                        if specs.has_key(service_uid):
                            references[reference_uid]['services'].append(service_uid)
                            references[reference_uid]['count'] += 1
                    if references[reference_uid]['count'] == len(wst_service_uids):
                        complete_reference_found = True
                        break
                if complete_reference_found:
                    ws.addReferences(int(row['pos']),
                                     reference,
                                     wst_service_uids)
                else:
                    # find the most complete reference sample instead
                    these_services = wst_service_uids
                    reference_keys = references.keys()
                    no_of_services = 0
                    reference = None
                    for key in reference_keys:
                        if references[key]['count'] > no_of_services:
                            no_of_services = references[key]['count']
                            reference = key
                    if reference:
                        ws.addReferences(int(row['pos']),
                                         rc.lookupObject(reference),
                                         wst_service_uids)

        # fill duplicate positions
        layout = ws.getLayout()
        for row in [r for r in wstlayout if r['type'] == 'd']:
            dest_pos = int(row['pos'])
            src_pos = int(row['dup'])
            if src_pos in [int(slot['position']) for slot in layout]:
                ws.addDuplicateAnalyses(src_pos, dest_pos)

        if ws.getLayout():
            self.request.RESPONSE.redirect(ws.absolute_url() + "/manage_results")
        else:
            self.context.plone_utils.addPortalMessage(_("No analyses were added to this worksheet."))
            self.request.RESPONSE.redirect(ws.absolute_url() + "/add_analyses")
