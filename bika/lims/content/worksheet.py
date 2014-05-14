from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.fields import HistoryAwareReferenceField
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IWorksheet
from bika.lims.permissions import EditWorksheet
from bika.lims.workflow import doActionFor
from bika.lims.workflow import skip
from DateTime import DateTime
from operator import itemgetter
from plone.indexer import indexer
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATExtensions.ateapi import RecordsField
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode, _createObjectByType
from zope.interface import implements

@indexer(IWorksheet)
def Priority(instance):
    priority = instance.getPriority()
    if priority:
        return priority.getSortKey()


schema = BikaSchema.copy() + Schema((
    HistoryAwareReferenceField('WorksheetTemplate',
        allowed_types=('WorksheetTemplate',),
        relationship='WorksheetAnalysisTemplate',
    ),
    ComputedField('WorksheetTemplateTitle',
        searchable=True,
        expression="context.getWorksheetTemplate() and context.getWorksheetTemplate().Title() or ''",
        widget=ComputedWidget(
            visible=False,
        ),
    ),
    RecordsField('Layout',
        required=1,
        subfields=('position', 'type', 'container_uid', 'analysis_uid'),
        subfield_types={'position': 'int'},
    ),
    # all layout info lives in Layout; Analyses is used for back references.
    ReferenceField('Analyses',
        required=1,
        multiValued=1,
        allowed_types=('Analysis', 'DuplicateAnalysis', 'ReferenceAnalysis',),
        relationship = 'WorksheetAnalysis',
    ),
    StringField('Analyst',
        searchable = True,
    ),
    # TODO Remove. Instruments must be assigned directly to each analysis.
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
            macro="bika_widgets/remarks",
            label=_('Remarks'),
            append_only=True,
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

    def addAnalysis(self, analysis, position=None):
        """- add the analysis to self.Analyses().
           - position is overruled if a slot for this analysis' parent exists
           - if position is None, next available pos is used.
        """
        workflow = getToolByName(self, 'portal_workflow')

        analysis_uid = analysis.UID()
        parent_uid = analysis.aq_parent.UID()
        analyses = self.getAnalyses()
        layout = self.getLayout()

        # check if this analysis is already in the layout
        if analysis_uid in [l['analysis_uid'] for l in layout]:
            return

        # If the ws has an instrument assigned for which the analysis
        # is allowed, set it
        instr = self.getInstrument()
        if instr and analysis.isInstrumentAllowed(instr):
            # Set the method assigned to the selected instrument
            analysis.setMethod(instr.getMethod())
            analysis.setInstrument(instr)

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

        allowed_transitions = [t['id'] for t in workflow.getTransitionsFor(analysis)]
        if 'assign' in allowed_transitions:
            workflow.doActionFor(analysis, 'assign')

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
                dma = analysis.aq_parent.getAnalyses(getKeyword=dmk,
                                                     full_objects=True)[0]
                # add it.
                if dma not in self.getAnalyses():
                    self.addAnalysis(dma)

    security.declareProtected(EditWorksheet, 'removeAnalysis')

    def removeAnalysis(self, analysis):
        """ delete an analyses from the worksheet and un-assign it
        """
        workflow = getToolByName(self, 'portal_workflow')

        # overwrite saved context UID for event subscriber
        self.REQUEST['context_uid'] = self.UID()
        workflow.doActionFor(analysis, 'unassign')
        # Note: subscriber might unassign the AR and/or promote the worksheet

        # remove analysis from context.Analyses *after* unassign,
        # (doActionFor requires worksheet in analysis.getBackReferences)
        Analyses = self.getAnalyses()
        if analysis in Analyses:
            Analyses.remove(analysis)
            self.setAnalyses(Analyses)
        layout = [slot for slot in self.getLayout() if slot['analysis_uid'] != analysis.UID()]
        self.setLayout(layout)

        if analysis.portal_type == "DuplicateAnalysis":
            self._delObject(analysis.id)

    def addReferences(self, position, reference, service_uids):
        """ Add reference analyses to reference, and add to worksheet layout
        """
        workflow = getToolByName(self, 'portal_workflow')
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

        postfix = 1
        for refa in reference.getReferenceAnalyses():
            grid = refa.getReferenceAnalysesGroupID()
            try:
                cand = int(grid.split('-')[2])
                if cand >= postfix:
                    postfix = cand + 1
            except:
                pass
        postfix = str(postfix).zfill(int(3))
        refgid = '%s-%s' % (reference.id, postfix)
        for service_uid in service_uids:
            # services with dependents don't belong in references
            service = rc.lookupObject(service_uid)
            calc = service.getCalculation()
            if calc and calc.getDependentServices():
                continue
            ref_uid = reference.addReferenceAnalysis(service_uid, ref_type)
            ref_analysis = rc.lookupObject(ref_uid)

            # Set ReferenceAnalysesGroupID (same id for the analyses from
            # the same Reference Sample and same Worksheet)
            # https://github.com/bikalabs/Bika-LIMS/issues/931
            ref_analysis.setReferenceAnalysesGroupID(refgid)
            ref_analysis.reindexObject(idxs=["getReferenceAnalysesGroupID"])

            # copy the interimfields
            if calc:
                ref_analysis.setInterimFields(calc.getInterimFields())

            self.setLayout(
                self.getLayout() + [{'position': position,
                                     'type': ref_type,
                                     'container_uid': reference.UID(),
                                     'analysis_uid': ref_analysis.UID()}])
            self.setAnalyses(
                self.getAnalyses() + [ref_analysis, ])
            workflow.doActionFor(ref_analysis, 'assign')

    security.declareProtected(EditWorksheet, 'addDuplicateAnalyses')

    def addDuplicateAnalyses(self, src_slot, dest_slot):
        """ add duplicate analyses to worksheet
        """
        rc = getToolByName(self, REFERENCE_CATALOG)
        workflow = getToolByName(self, 'portal_workflow')

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

        src_analyses = [rc.lookupObject(slot['analysis_uid'])
                        for slot in layout if
                        int(slot['position']) == int(src_slot)]
        dest_analyses = [rc.lookupObject(slot['analysis_uid']).getAnalysis().UID()
                        for slot in layout if
                        int(slot['position']) == int(dest_slot)]

        refgid = None
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
            duplicate = _createObjectByType("DuplicateAnalysis", self, _id)
            duplicate.setAnalysis(analysis)

            # Set ReferenceAnalysesGroupID (same id for the analyses from
            # the same Reference Sample and same Worksheet)
            # https://github.com/bikalabs/Bika-LIMS/issues/931
            if not refgid and not analysis.portal_type == 'ReferenceAnalysis':
                part = analysis.getSamplePartition().id
                dups = [an.getReferenceAnalysesGroupID()
                        for an in self.getAnalyses()
                        if an.portal_type == 'DuplicateAnalysis'
                            and an.getSamplePartition().id == part]
                dups = list(set(dups))
                postfix = dups and len(dups) + 1 or 1
                postfix = str(postfix).zfill(int(2))
                refgid = '%s-D%s' % (part, postfix)
            duplicate.setReferenceAnalysesGroupID(refgid)
            duplicate.reindexObject(idxs=["getReferenceAnalysesGroupID"])

            duplicate.processForm()
            if calc:
                duplicate.setInterimFields(calc.getInterimFields())
            self.setLayout(
                self.getLayout() + [{'position': dest_slot,
                                     'type': 'd',
                                     'container_uid': analysis.aq_parent.UID(),
                                     'analysis_uid': duplicate.UID()}, ]
            )
            self.setAnalyses(self.getAnalyses() + [duplicate, ])
            workflow.doActionFor(duplicate, 'assign')

    def applyWorksheetTemplate(self, wst):
        """ Add analyses to worksheet according to wst's layout.
            Will not overwrite slots which are filled already.
            If the selected template has an instrument assigned, it will
            only be applied to those analyses for which the instrument
            is allowed
        """
        rc = getToolByName(self, REFERENCE_CATALOG)
        bac = getToolByName(self, "bika_analysis_catalog")
        bc = getToolByName(self, 'bika_catalog')

        layout = self.getLayout()
        wstlayout = wst.getLayout()
        services = wst.getService()
        wst_service_uids = [s.UID() for s in services]

        analyses = bac(portal_type='Analysis',
                       getServiceUID=wst_service_uids,
                       review_state='sample_received',
                       worksheetanalysis_review_state='unassigned',
                       cancellation_state = 'active')
        sortedans = []
        for an in analyses:
            sortedans.append({'uid': an.UID,
                              'duedate': an.getObject().getDueDate() or (DateTime() + 365),
                              'brain': an});
        sortedans.sort(key=itemgetter('duedate'), reverse=False)
        # collect analyses from the first X ARs.
        ar_analyses = {}  # ar_uid : [analyses]
        ars = []  # for sorting

        wst_slots = [row['pos'] for row in wstlayout if row['type'] == 'a']
        ws_slots = [row['position'] for row in layout if row['type'] == 'a']
        nr_slots = len(wst_slots) - len(ws_slots)
        instr = self.getInstrument()
        for analysis in sortedans:
            analysis = analysis['brain']
            if instr and analysis.getObject().isInstrumentAllowed(instr) == False:
                # Exclude those analyses for which the ws selected
                # instrument is not allowed
                continue
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
                self.addAnalysis(analysis, position=positions[ars.index(ar)])

        # find best maching reference samples for Blanks and Controls
        for t in ('b', 'c'):
            form_key = t == 'b' and 'blank_ref' or 'control_ref'
            ws_slots = [row['position'] for row in layout if row['type'] == t]
            for row in [r for r in wstlayout if
                        r['type'] == t and r['pos'] not in ws_slots]:
                reference_definition_uid = row[form_key]
                samples = bc(portal_type='ReferenceSample',
                             review_state='current',
                             inactive_state='active',
                             getReferenceDefinitionUID=reference_definition_uid)
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
                        if service_uid in specs:
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

    def exportAnalyses(self, REQUEST=None, RESPONSE=None):
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

    def resequenceWorksheet(self, REQUEST=None, RESPONSE=None):
        """  Reset the sequence of analyses in the worksheet """
        """ sequence is [{'pos': , 'type': , 'uid', 'key'},] """
        old_seq = self.getLayout()
        new_dict = {}
        new_seq = []
        other_dict = {}
        for seq in old_seq:
            if seq['key'] == '':
                if seq['pos'] not in other_dict:
                    other_dict[seq['pos']] = []
                other_dict[seq['pos']].append(seq)
                continue
            if seq['key'] not in new_dict:
                new_dict[seq['key']] = []
            analyses = new_dict[seq['key']]
            analyses.append(seq)
            new_dict[seq['key']] = analyses
        new_keys = sorted(new_dict.keys())

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
                a_keys = sorted(analyses.keys())
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

    def setInstrument(self, instrument):
        """ Sets the specified instrument to the Analysis from the
            Worksheet. Only sets the instrument if the Analysis
            allows it, according to its Analysis Service and Method.
            If an analysis has already assigned an instrument, it won't
            be overriden.
            The Analyses that don't allow the instrument specified will
            not be modified.
            Returns the number of analyses affected
        """
        analyses = [an for an in self.getAnalyses()
                    if not an.getInstrument()
                        and an.isInstrumentAllowed(instrument)]
        total = 0
        for an in analyses:
            success = an.setInstrument(instrument)
            if success is True:
                total += 1

        self.getField('Instrument').set(self, instrument)
        return total

    def workflow_script_submit(self):
        # Don't cascade. Shouldn't be submitting WSs directly for now,
        # except edge cases where all analyses are already submitted,
        # but self was held back until an analyst was assigned.
        workflow = getToolByName(self, 'portal_workflow')
        self.reindexObject(idxs=["review_state", ])
        can_attach = True
        for a in self.getAnalyses():
            if workflow.getInfoFor(a, 'review_state') in \
               ('to_be_sampled', 'to_be_preserved', 'sample_due',
                'sample_received', 'attachment_due', 'assigned',):
                # Note: referenceanalyses and duplicateanalyses can still have review_state = "assigned".
                can_attach = False
                break
        if can_attach:
            doActionFor(self, 'attach')

    def workflow_script_attach(self):
        if skip(self, "attach"):
            return
        self.reindexObject(idxs=["review_state", ])
        # Don't cascade. Shouldn't be attaching WSs for now (if ever).
        return

    def workflow_script_retract(self):
        if skip(self, "retract"):
            return
        workflow = getToolByName(self, 'portal_workflow')
        self.reindexObject(idxs=["review_state", ])
        if not "retract all analyses" in self.REQUEST['workflow_skiplist']:
            # retract all analyses in this self.
            # (NB: don't retract if it's verified)
            analyses = self.getAnalyses()
            for analysis in analyses:
                if workflow.getInfoFor(analysis, 'review_state', '') not in ('attachment_due', 'to_be_verified',):
                    continue
                doActionFor(analysis, 'retract')

    def workflow_script_verify(self):
        if skip(self, "verify"):
            return
        workflow = getToolByName(self, 'portal_workflow')
        self.reindexObject(idxs=["review_state", ])
        if not "verify all analyses" in self.REQUEST['workflow_skiplist']:
            # verify all analyses in this self.
            analyses = self.getAnalyses()
            for analysis in analyses:
                if workflow.getInfoFor(analysis, 'review_state', '') != 'to_be_verified':
                    continue
                doActionFor(analysis, "verify")

    def getPriority(self):
        """ get highest priority from all analyses
        """
        analyses = self.getAnalyses()
        priorities = []
        for analysis in analyses:
            if analysis.getPriority():
                priorities.append(analysis.getPriority())
        priorities = sorted(priorities, key = itemgetter('sortKey'))
        if priorities:
            return priorities[-1]

registerType(Worksheet, PROJECTNAME)
