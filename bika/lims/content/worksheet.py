from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.CMFCore.permissions import ListFolderContents, View
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Archetypes.public import *
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.Registry import registerField
from bika.lims.browser.fields import HistoryAwareReferenceField
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import PROJECTNAME
from bika.lims.permissions import EditWorksheet
from Products.ATExtensions.ateapi import RecordsField
from zope.interface import implements
from bika.lims.interfaces import IWorksheet
from bika.lims import bikaMessageFactory as _
from Products.Archetypes.references import HoldingReference
from bika.lims import logger

schema = BikaSchema.copy() + Schema((
    HistoryAwareReferenceField('WorksheetTemplate',
        allowed_types = ('WorksheetTemplate',),
        relationship = 'WorksheetAnalysisTemplate',
    ),
    ComputedField('WorksheetTemplateTitle',
        searchable = True,
        expression = "context.getWorksheetTemplate() and context.getWorksheetTemplate().Title() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    RecordsField('Layout',
        required = 1,
        subfields = ('position', 'type', 'container_uid', 'analysis_uid'),
        subfield_types = {'position':'int'},
    ),
    # all layout info lives in Layout; Analyses is used for back references.
    ReferenceField('Analyses',
        required = 1,
        multiValued = 1,
        allowed_types = ('Analysis', 'DuplicateAnalysis', 'ReferenceAnalysis',),
        relationship = 'WorksheetAnalysis',
    ),
    StringField('Analyst',
        searchable = True,
    ),
    ReferenceField('Instrument',
        required = 0,
        allowed_types = ('Instrument',),
        relationship = 'WorksheetInstrument',
        referenceClass = HoldingReference,
    ),
    TextField('Remarks',
        searchable = True,
        default_content_type = 'text/plain',
        allowed_content_types= ('text/plain', ),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            macro = "bika_widgets/remarks",
            label = _('Remarks'),
            append_only = True,
        ),
    ),
),
)

schema['id'].required = 0
schema['id'].widget.visible = False
schema['title'].required = 0
schema['title'].widget.visible = {'edit': 'hidden', 'view': 'invisible'}

class Worksheet(BaseFolder, HistoryAwareMixin):
    security = ClassSecurityInfo()
    implements(IWorksheet)
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        return safe_unicode(self.getId()).encode('utf-8')

    def getFolderContents(self, contentFilter):
        # The bika_listing machine passes contentFilter to all
        # contentsMethod methods.  We ignore it.
        return list(self.getAnalyses())

    security.declareProtected(EditWorksheet, 'addAnalysis')
    def addAnalysis(self, analysis, position = None):
        """- add the analysis to self.Analyses().
           - position is overruled if a slot for this analysis' parent exists
           - if position is None, next available pos is used.
        """
        wf = getToolByName(self, 'portal_workflow')

        analysis_uid = analysis.UID()
        parent_uid = analysis.aq_parent.UID()
        analyses = self.getAnalyses()
        layout = self.getLayout()

        # check if this analysis is already in the layout
        if analysis_uid in [l['analysis_uid'] for l in layout]:
            return

        self.setAnalyses(analyses + [analysis, ])

        # if our parent has a position, use that one.
        if analysis.aq_parent.UID() in [slot['container_uid'] for slot in layout]:
            position = [int(slot['position']) for slot in layout if
                        slot['container_uid'] == analysis.aq_parent.UID()][0]
        else:
            # prefer supplied position parameter
            if not position:
                used_positions = [0, ] + [int(slot['position']) for slot in layout]
                position = [pos for pos in range(1, max(used_positions) + 2)
                            if pos not in used_positions][0]
        self.setLayout(layout + [{'position': position,
                                  'type': 'a',
                                  'container_uid': parent_uid,
                                  'analysis_uid': analysis.UID()}, ])
        wf.doActionFor(analysis, 'assign')

        # If a dependency of DryMatter service is added here, we need to
        # make sure that the dry matter analysis itself is also
        # present.  Otherwise WS calculations refer to the DB version
        # of the DM analysis, which is out of sync with the form.
        dms = self.bika_setup.getDryMatterService()
        if dms:
            dmk = dms.getKeyword()
            deps = analysis.getDependents()
            # if dry matter service in my dependents:
            if dmk in [a.getService().getKeyword() for a in deps]:
                # get dry matter analysis from AR
                dma = analysis.aq_parent.getAnalyses(getKeyword = dmk,
                                                     full_objects = True)[0]
                # add it.
                if dma not in self.getAnalyses():
                    self.addAnalysis(dma)

    security.declareProtected(EditWorksheet, 'removeAnalysis')
    def removeAnalysis(self, analysis):
        """ delete an analyses from the worksheet and un-assign it
        """
        wf = getToolByName(self, 'portal_workflow')
        Analyses = self.getAnalyses()
        if analysis in Analyses:
            Analyses.remove(analysis)
            self.setAnalyses(Analyses)
        layout = [slot for slot in self.getLayout() if slot['analysis_uid'] != analysis.UID()]
        self.setLayout(layout)

        # overwrite saved context UID for event subscriber
        self.REQUEST['context_uid'] = self.UID()
        wf.doActionFor(analysis, 'unassign')
        # Note: subscriber might unassign the AR and/or promote the worksheet

        if analysis.portal_type == "DuplicateAnalysis":
            self._delObject(analysis.id)

    def addReferences(self, position, reference, service_uids):
        """ Add reference analyses to reference, and add to worksheet layout
        """
        wf = getToolByName(self, 'portal_workflow')
        rc = getToolByName(self, REFERENCE_CATALOG)
        layout = self.getLayout()
        wst = self.getWorksheetTemplate()
        wstlayout = wst and wst.getLayout() or []
        ref_type = reference.getBlank() and 'b' or 'c'
        ref_uid = reference.UID()

        if position == 'new':
            highest_existing_position = len(wstlayout)
            for pos in [int(slot['position']) for slot in layout]:
                if pos > highest_existing_position:
                    highest_existing_position = pos
            position = highest_existing_position + 1

        for service_uid in service_uids:
            # services with dependents don't belong in references
            service = rc.lookupObject(service_uid)
            calc = service.getCalculation()
            if calc and calc.getDependentServices():
                continue
            ref_uid = reference.addReferenceAnalysis(service_uid, ref_type)
            ref_analysis = rc.lookupObject(ref_uid)

            # copy the interimfields
            calculation = service.getCalculation()
            if calc:
                ref_analysis.setInterimFields(calc.getInterimFields())

            self.setLayout(
                self.getLayout() + [{'position' : position,
                                     'type':ref_type,
                                     'container_uid' : reference.UID(),
                                     'analysis_uid': ref_analysis.UID()}])
            self.setAnalyses(
                self.getAnalyses() + [ref_analysis, ])
            wf.doActionFor(ref_analysis, 'assign')


    security.declareProtected(EditWorksheet, 'addDuplicateAnalyses')
    def addDuplicateAnalyses(self, src_slot, dest_slot):
        """ add duplicate analyses to worksheet
        """
        rc = getToolByName(self, REFERENCE_CATALOG)
        wf = getToolByName(self, 'portal_workflow')

        layout = self.getLayout()
        wst = self.getWorksheetTemplate()
        wstlayout = wst and wst.getLayout() or []

        src_ar = [slot['container_uid'] for slot in layout if
                  slot['position'] == src_slot]
        if src_ar:
            src_ar = src_ar[0]

        if not dest_slot or dest_slot == 'new':
            highest_existing_position = len(wstlayout)
            for pos in [int(slot['position']) for slot in layout]:
                if pos > highest_existing_position:
                    highest_existing_position = pos
            dest_slot = highest_existing_position + 1

        src_analyses = [rc.lookupObject(slot['analysis_uid']) \
                        for slot in layout if \
                        int(slot['position']) == int(src_slot)]
        dest_analyses = [rc.lookupObject(slot['analysis_uid']).getAnalysis().UID() \
                        for slot in layout if \
                        int(slot['position']) == int(dest_slot)]

        for analysis in src_analyses:
            if analysis.UID() in dest_analyses:
                continue
            # services with dependents don't belong in duplicates
            service = analysis.getService()
            calc = service.getCalculation()
            if calc and calc.getDependentServices():
                continue
            service = analysis.getService()
            _id = self._findUniqueId(service.getKeyword())
            self.invokeFactory('DuplicateAnalysis', id = _id)
            duplicate = self[_id]
            duplicate.setAnalysis(analysis)
            duplicate.processForm()
            if calc:
                duplicate.setInterimFields(calc.getInterimFields())
            self.setLayout(
                self.getLayout() + [{'position':dest_slot,
                                     'type':'d',
                                     'container_uid':analysis.aq_parent.UID(),
                                     'analysis_uid': duplicate.UID()}, ]
            )
            self.setAnalyses(self.getAnalyses() + [duplicate, ])
            wf.doActionFor(duplicate, 'assign')

    def applyWorksheetTemplate(self, wst):
        """ Add analyses to worksheet according to wst's layout.
            Will not overwrite slots which are filled already.
        """
        rc = getToolByName(self, REFERENCE_CATALOG)
        bac = getToolByName(self, "bika_analysis_catalog")
        bc = getToolByName(self, 'bika_catalog')

        layout = self.getLayout()
        wstlayout = wst.getLayout()
        services = wst.getService()
        wst_service_uids = [s.UID() for s in services]

        analyses = bac(portal_type = 'Analysis',
                       getServiceUID = wst_service_uids,
                       review_state = 'sample_received',
                       worksheetanalysis_review_state = 'unassigned',
                       cancellation_state = 'active',
                       sort_on = 'getDueDate')
        # collect analyses from the first X ARs.
        ar_analyses = {} # ar_uid : [analyses]
        ars = [] # for sorting

        wst_slots = [row['pos'] for row in wstlayout if row['type'] == 'a']
        ws_slots = [row['position'] for row in layout if row['type'] == 'a']
        nr_slots = len(wst_slots) - len(ws_slots)
        for analysis in analyses:
            ar = analysis.getRequestID
            if ar in ar_analyses:
                ar_analyses[ar].append(analysis.getObject())
            else:
                if len(ar_analyses.keys()) < nr_slots:
                    ars.append(ar)
                    ar_analyses[ar] = [analysis.getObject(), ]

        positions = [pos for pos in wst_slots if pos not in ws_slots]
        for ar in ars:
            for analysis in ar_analyses[ar]:
                self.addAnalysis(analysis, position = positions[ars.index(ar)])

        # find best maching reference samples for Blanks and Controls
        for t in ('b', 'c'):
            form_key = t == 'b' and 'blank_ref' or 'control_ref'
            ws_slots = [row['position'] for row in layout if row['type'] == t]
            for row in [r for r in wstlayout if
                        r['type'] == t and r['pos'] not in ws_slots]:
                reference_definition_uid = row[form_key]
                samples = bc(portal_type = 'ReferenceSample',
                             review_state = 'current',
                             inactive_state = 'active',
                             getReferenceDefinitionUID = reference_definition_uid)
                if not samples:
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
                    self.addReferences(int(row['pos']),
                                     reference,
                                     wst_service_uids)
                else:
                    # find the most complete reference sample instead
                    reference_keys = references.keys()
                    no_of_services = 0
                    reference = None
                    for key in reference_keys:
                        if references[key]['count'] > no_of_services:
                            no_of_services = references[key]['count']
                            reference = key
                    if reference:
                        self.addReferences(int(row['pos']),
                                         rc.lookupObject(reference),
                                         wst_service_uids)

        # fill duplicate positions
        layout = self.getLayout()
        ws_slots = [row['position'] for row in layout if row['type'] == 'd']
        for row in [r for r in wstlayout if
                    r['type'] == 'd' and r['pos'] not in ws_slots]:
            dest_pos = int(row['pos'])
            src_pos = int(row['dup'])
            if src_pos in [int(slot['position']) for slot in layout]:
                self.addDuplicateAnalyses(src_pos, dest_pos)


    def exportAnalyses(self, REQUEST = None, RESPONSE = None):
        """ Export analyses from this worksheet """
        import bika.lims.InstrumentExport as InstrumentExport
        instrument = REQUEST.form['getInstrument']
        try:
            func = getattr(InstrumentExport, "%s_export" % instrument)
        except:
            return
        func(self, REQUEST, RESPONSE)
        return

    security.declarePublic('getWorksheetServices')
    def getWorksheetServices(self):
        """ get list of analysis services present on this worksheet
        """
        services = []
        for analysis in self.getAnalyses():
            service = analysis.getService()
            if service not in services:
                services.append(service)
        return services

    security.declareProtected(EditWorksheet, 'resequenceWorksheet')
    def resequenceWorksheet(self, REQUEST = None, RESPONSE = None):
        """  Reset the sequence of analyses in the worksheet """
        """ sequence is [{'pos': , 'type': , 'uid', 'key'},] """
        old_seq = self.getLayout()
        new_dict = {}
        new_seq = []
        other_dict = {}
        for seq in old_seq:
            if seq['key'] == '':
                if not other_dict.has_key(seq['pos']):
                    other_dict[seq['pos']] = []
                other_dict[seq['pos']].append(seq)
                continue
            if not new_dict.has_key(seq['key']):
                new_dict[seq['key']] = []
            analyses = new_dict[seq['key']]
            analyses.append(seq)
            new_dict[seq['key']] = analyses
        new_keys = new_dict.keys()
        new_keys.sort()

        rc = getToolByName(self, REFERENCE_CATALOG)
        seqno = 1
        for key in new_keys:
            analyses = {}
            if len(new_dict[key]) == 1:
                new_dict[key][0]['pos'] = seqno
                new_seq.append(new_dict[key][0])
            else:
                for item in new_dict[key]:
                    item['pos'] = seqno
                    analysis = rc.lookupObject(item['uid'])
                    service = analysis.Title()
                    analyses[service] = item
                a_keys = analyses.keys()
                a_keys.sort()
                for a_key in a_keys:
                    new_seq.append(analyses[a_key])
            seqno += 1
        other_keys = other_dict.keys()
        other_keys.sort()
        for other_key in other_keys:
            for item in other_dict[other_key]:
                item['pos'] = seqno
                new_seq.append(item)
            seqno += 1

        self.setLayout(new_seq)
        RESPONSE.redirect('%s/manage_results' % self.absolute_url())

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()

registerType(Worksheet, PROJECTNAME)
