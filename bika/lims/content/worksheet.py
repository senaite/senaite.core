# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import re

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType, safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims import deprecated
from bika.lims import logger
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.config import *
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IDuplicateAnalysis
from bika.lims.interfaces import IReferenceAnalysis
from bika.lims.interfaces import IWorksheet
from bika.lims.permissions import EditWorksheet, ManageWorksheets
from bika.lims.permissions import Verify as VerifyPermission
from bika.lims.utils import changeWorkflowState, tmpID
from bika.lims.utils import to_utf8 as _c
from bika.lims.workflow import doActionFor
from bika.lims.workflow import skip
from bika.lims.workflow.worksheet import events
from bika.lims.workflow.worksheet import guards
from plone import api
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    UIDReferenceField(
        'WorksheetTemplate',
        allowed_types=('WorksheetTemplate',),
    ),
    RecordsField('Layout',
        required=1,
        subfields=('position', 'type', 'container_uid', 'analysis_uid'),
        subfield_types={'position': 'int'},
    ),
    # all layout info lives in Layout; Analyses is used for back references.
    UIDReferenceField('Analyses',
        required=1,
        multiValued=1,
        allowed_types=('Analysis', 'DuplicateAnalysis', 'ReferenceAnalysis', 'RejectAnalysis'),
    ),
    StringField('Analyst',
        searchable = True,
    ),
    UIDReferenceField(
        'Method',
        required=0,
        vocabulary='_getMethodsVoc',
        allowed_types=('Method',),
        widget=SelectionWidget(
            format='select',
            label=_("Method"),
            visible=False,
        ),
    ),
    # TODO Remove. Instruments must be assigned directly to each analysis.
    UIDReferenceField('Instrument',
        required = 0,
        allowed_types = ('Instrument',),
        vocabulary = '_getInstrumentsVoc',
    ),
    TextField('Remarks',
        searchable = True,
        default_content_type = 'text/plain',
        allowed_content_types= ('text/plain', ),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            macro="bika_widgets/remarks",
            label=_("Remarks"),
            append_only=True,
        ),
    ),
    StringField('ResultsLayout',
        default = '1',
        vocabulary = WORKSHEET_LAYOUT_OPTIONS,
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

    def setWorksheetTemplate(self, worksheettemplate, **kw):
        """
        Once a worksheettemplate has been set, the function looks for the
        method of the template, if there is one, the function sets the
        method field of the worksheet.
        """
        self.getField('WorksheetTemplate').set(self, worksheettemplate)
        if worksheettemplate and isinstance(worksheettemplate, str):
            # worksheettemplate is a UID, so we need to get the object first
            uc = getToolByName(self, 'uid_catalog')
            wst = uc(UID=worksheettemplate)
            if wst and len(wst) == 1:
                self.setMethod(wst[0].getObject().getRestrictToMethod())
            else:
                logger.warning(
                    'The given Worksheet Template UID "%s" to be set ' +
                    'in the Worksheet Object "%s" with uid "%s" is not valid' %
                    (worksheettemplate, self.Title(), self.UID()))
        elif worksheettemplate and worksheettemplate.getRestrictToMethod():
            self.setMethod(worksheettemplate.getRestrictToMethod())

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
            # TODO After enabling multiple methods for instruments, we are
            # setting intrument's first method as a method.
            methods = instr.getMethods()
            if len(methods) > 0:
                # Set the first method assigned to the selected instrument
                analysis.setMethod(methods[0])
            analysis.setInstrument(instr)
        # If the ws DOESN'T have an instrument assigned but it has a method,
        # set the method to the analysis
        method = self.getMethod()
        if not instr and method and analysis.isMethodAllowed(method):
            # Set the method
            analysis.setMethod(method)
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

        doActionFor(analysis, 'assign')

        # If a dependency of DryMatter service is added here, we need to
        # make sure that the dry matter analysis itself is also
        # present.  Otherwise WS calculations refer to the DB version
        # of the DM analysis, which is out of sync with the form.
        dms = self.bika_setup.getDryMatterService()
        if dms:
            dmk = dms.getKeyword()
            deps = analysis.getDependents()
            # if dry matter service in my dependents:
            if dmk in [a.getKeyword() for a in deps]:
                # get dry matter analysis from AR
                dma = analysis.aq_parent.getAnalyses(getKeyword=dmk,
                                                     full_objects=True)[0]
                # add it.
                if dma not in self.getAnalyses():
                    self.addAnalysis(dma)
        # Reindex the worksheet in order to update its columns
        self.reindexObject()
        analysis.reindexObject(idxs=['getWorksheetUID',])

    security.declareProtected(EditWorksheet, 'removeAnalysis')

    def removeAnalysis(self, analysis):
        """ delete an analyses from the worksheet and un-assign it
        """
        workflow = getToolByName(self, 'portal_workflow')

        # overwrite saved context UID for event subscriber
        self.REQUEST['context_uid'] = self.UID()
        doActionFor(analysis, 'unassign')

        # remove analysis from context.Analyses *after* unassign,
        # (doActionFor requires worksheet in analysis.getBackReferences)
        Analyses = self.getAnalyses()
        if analysis in Analyses:
            Analyses.remove(analysis)
            self.setAnalyses(Analyses)
            analysis.reindexObject()
        layout = [
            slot for slot in self.getLayout()
            if slot['analysis_uid'] != analysis.UID()]
        self.setLayout(layout)

        if analysis.portal_type == "DuplicateAnalysis":
            self.manage_delObjects(ids=[analysis.id])
        # Reindex the worksheet in order to update its columns
        self.reindexObject()

    def _getMethodsVoc(self):
        """
        This function returns the registered methods in the system as a
        vocabulary.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(i.UID, i.Title)
                 for i in bsc(portal_type='Method',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        items.insert(0, ('', _("Not specified")))
        return DisplayList(list(items))

    def _getInstrumentsVoc(self):
        """
        This function returns the registered instruments in the system as a
        vocabulary. The instruments are filtered by the selected method.
        """
        cfilter = {'portal_type': 'Instrument', 'inactive_state': 'active'}
        if self.getMethod():
            cfilter['getMethodUIDs'] = {"query": self.getMethod().UID(),
                                        "operator": "or"}
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('', 'No instrument')] + [
            (o.UID, o.Title) for o in
            bsc(cfilter)]
        o = self.getInstrument()
        if o and o.UID() not in [i[0] for i in items]:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

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

        # LIMS-2132 Reference Analyses got the same ID
        refgid = self.nextReferenceAnalysesGroupID(reference)

        for service_uid in service_uids:
            # services with dependents don't belong in references
            service = rc.lookupObject(service_uid)
            calc = service.getCalculation()
            if calc and calc.getDependentServices():
                continue
            ref_uid = reference.addReferenceAnalysis(service_uid, ref_type)
            ref_analysis = rc.lookupObject(ref_uid)

            # Set the required number of verifications
            reqvers = service.getNumberOfRequiredVerifications()
            ref_analysis.setNumberOfRequiredVerifications(reqvers)

            # Set ReferenceAnalysesGroupID (same id for the analyses from
            # the same Reference Sample and same Worksheet)
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
            doActionFor(ref_analysis, 'assign')
            # Reindex the worksheet in order to update its columns
            self.reindexObject()

    def nextReferenceAnalysesGroupID(self, reference):
        """ Returns the next ReferenceAnalysesGroupID for the given reference
            sample. Gets the last reference analysis registered in the system
            for the specified reference sample and increments in one unit the
            suffix.
        """
        bac = getToolByName(reference, 'bika_analysis_catalog')
        ids = bac.Indexes['getReferenceAnalysesGroupID'].uniqueValues()
        prefix = reference.id+"-"
        rr = re.compile("^"+prefix+"[\d+]+$")
        ids = [int(i.split(prefix)[1]) for i in ids if i and rr.match(i)]
        ids.sort()
        _id = ids[-1] if ids else 0
        suffix = str(_id+1).zfill(int(3))
        return '%s%s' % (prefix, suffix)

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
        processed = []
        for analysis in src_analyses:
            if analysis.UID() in dest_analyses:
                continue
            if analysis.portal_type == 'ReferenceAnalysis':
                logger.warning('Cannot create duplicate analysis from '
                               'ReferenceAnalysis at {}'.format(analysis))
                continue

            # If retracted analyses, for some reason, the getLayout() returns
            # two times the regular analysis generated automatically after a
            # a retraction.
            if analysis.UID() in processed:
                continue

            # Omit retracted analyses
            # https://jira.bikalabs.com/browse/LIMS-1745
            # https://jira.bikalabs.com/browse/LIMS-2001
            if workflow.getInfoFor(analysis, "review_state") == 'retracted':
                continue

            processed.append(analysis.UID())

            # services with dependents don't belong in duplicates
            calc = analysis.getCalculation()
            if calc and calc.getDependentServices():
                continue
            duplicate = _createObjectByType("DuplicateAnalysis", self, tmpID())
            duplicate.setAnalysis(analysis)

            # Set the required number of verifications
            reqvers = analysis.getNumberOfRequiredVerifications()
            duplicate.setNumberOfRequiredVerifications(reqvers)

            # Set ReferenceAnalysesGroupID (same id for the analyses from
            # the same Reference Sample and same Worksheet)
            if not refgid:
                prefix = analysis.aq_parent.getSample().id
                dups = []
                for an in self.getAnalyses():
                    if an.portal_type == 'DuplicateAnalysis' \
                            and hasattr(an.aq_parent, 'getSample') \
                            and an.aq_parent.getSample().id == prefix:
                        dups.append(an.getReferenceAnalysesGroupID())
                dups = list(set(dups))
                postfix = dups and len(dups) + 1 or 1
                postfix = str(postfix).zfill(int(2))
                refgid = '%s-D%s' % (prefix, postfix)
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
            doActionFor(duplicate, 'assign')


    def applyWorksheetTemplate(self, wst):
        """ Add analyses to worksheet according to wst's layout.
            Will not overwrite slots which are filled already.
            If the selected template has an instrument assigned, it will
            only be applied to those analyses for which the instrument
            is allowed, the same happens with methods.
        """
        rc = getToolByName(self, REFERENCE_CATALOG)
        bac = getToolByName(self, "bika_analysis_catalog")
        bc = getToolByName(self, 'bika_catalog')

        layout = self.getLayout()
        wstlayout = wst.getLayout()
        services = wst.getService()
        wst_service_uids = [s.UID() for s in services]
        wst_slots = [row['pos'] for row in wstlayout if row['type'] == 'a']
        ws_slots = [row['position'] for row in layout if row['type'] == 'a']
        nr_slots = len(wst_slots) - len(ws_slots)
        positions = [pos for pos in wst_slots if pos not in ws_slots]

        analyses = bac(portal_type='Analysis',
                       getServiceUID=wst_service_uids,
                       review_state='sample_received',
                       worksheetanalysis_review_state='unassigned',
                       cancellation_state = 'active',
                       sort_on='getDueDate')

        # ar_analyses is used to group analyses by AR.
        ar_analyses = {}
        instr = self.getInstrument() if self.getInstrument() else wst.getInstrument()
        method = wst.getRestrictToMethod()
        for brain in analyses:
            analysis = brain.getObject()
            if (instr and analysis.isInstrumentAllowed(instr) is False) or\
                    (method and analysis.isMethodAllowed(method) is False):
                # Exclude those analyses for which the ws selected
                # instrument or method is not allowed
                continue

            ar_id = brain.id
            if ar_id in ar_analyses:
                ar_analyses[ar_id].append(analysis)
            else:
                if len(ar_analyses.keys()) < nr_slots:
                    ar_analyses[ar_id] = [analysis, ]

        # Add analyses, sorted by AR ID
        ars = sorted(ar_analyses.keys())
        for ar in ars:
            for analysis in ar_analyses[ar]:
                self.addAnalysis(analysis, position=positions[ars.index(ar)])

        # find best maching reference samples for Blanks and Controls
        for t in ('b', 'c'):
            form_key = t == 'b' and 'blank_ref' or 'control_ref'
            ws_slots = [row['position'] for row in layout if row['type'] == t]
            for row in [r for r in wstlayout if
                        r['type'] == t and r['pos'] not in ws_slots]:
                reference_definition_uid = row.get(form_key, None)
                if (not reference_definition_uid):
                    continue
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
                    supported_uids = wst_service_uids
                    self.addReferences(int(row['pos']),
                                     reference,
                                     supported_uids)
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
                        reference = rc.lookupObject(reference)
                        supported_uids = [s.UID() for s in reference.getServices()
                                          if s.UID() in wst_service_uids]
                        self.addReferences(int(row['pos']),
                                         reference,
                                         supported_uids)

        # fill duplicate positions
        layout = self.getLayout()
        ws_slots = [row['position'] for row in layout if row['type'] == 'd']
        for row in [r for r in wstlayout if
                    r['type'] == 'd' and r['pos'] not in ws_slots]:
            dest_pos = int(row['pos'])
            src_pos = int(row['dup'])
            if src_pos in [int(slot['position']) for slot in layout]:
                self.addDuplicateAnalyses(src_pos, dest_pos)

        # Apply the wst instrument to all analyses and ws
        if instr:
            self.setInstrument(instr, True)
        # Apply the wst method to all analyses and ws
        if method:
            self.setMethod(method, True)

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

    def getInstrumentTitle(self):
        """
        Returns the instrument title
        :returns: instrument's title
        :rtype: string
        """
        instrument = self.getInstrument()
        if instrument:
            return instrument.Title()
        return ''

    def getWorksheetTemplateUID(self):
        """
        Returns the template's UID assigned to this worksheet
        :returns: worksheet's UID
        :rtype: UID as string
        """
        ws = self.getWorksheetTemplate()
        if ws:
            return ws.UID()
        return ''

    def getWorksheetTemplateTitle(self):
        """
        Returns the template's Title assigned to this worksheet
        :returns: worksheet's Title
        :rtype: string
        """
        ws = self.getWorksheetTemplate()
        if ws:
            return ws.Title()
        return ''

    def getWorksheetTemplateURL(self):
        """
        Returns the template's URL assigned to this worksheet
        :returns: worksheet's URL
        :rtype: string
        """
        ws = self.getWorksheetTemplate()
        if ws:
            return ws.absolute_url_path()
        return ''

    def getWorksheetServices(self):
        """get list of analysis services present on this worksheet
        """
        services = []
        for analysis in self.getAnalyses():
            service = analysis.getAnalysisService()
            if service and service not in services:
                services.append(service)
        return services

    def getQCAnalyses(self):
        """
        Return the Quality Control analyses.
        :returns: a list of QC analyses
        :rtype: List of ReferenceAnalysis/DuplicateAnalysis
        """
        qc_types = ['ReferenceAnalysis', 'DuplicateAnalysis']
        analyses = self.getAnalyses()
        return [a for a in analyses if a.portal_type in qc_types]

    def getDuplicateAnalyses(self):
        """Return the duplicate analyses assigned to the current worksheet
        :return: List of DuplicateAnalysis
        :rtype: List of IDuplicateAnalysis objects"""
        ans = self.getAnalyses()
        duplicates = [an for an in ans if IDuplicateAnalysis.providedBy(an)]
        return duplicates

    def getReferenceAnalyses(self):
        """Return the reference analyses (controls) assigned to the current
        worksheet
        :return: List of reference analyses
        :rtype: List of IReferenceAnalysis objects"""
        ans = self.getAnalyses()
        references = [an for an in ans if IReferenceAnalysis.providedBy(an)]
        return references

    def getRegularAnalyses(self):
        """
        Return the analyses assigned to the current worksheet that are directly
        associated to an Analysis Request but are not QC analyses. This is all
        analyses that implement IRoutineAnalysis
        :return: List of regular analyses
        :rtype: List of ReferenceAnalysis/DuplicateAnalysis
        """
        qc_types = ['ReferenceAnalysis', 'DuplicateAnalysis']
        analyses = self.getAnalyses()
        return [a for a in analyses if a.portal_type not in qc_types]

    def getNumberOfQCAnalyses(self):
        """
        Returns the number of Quality Control analyses.
        :returns: number of QC analyses
        :rtype: integer
        """
        return len(self.getQCAnalyses())

    def getNumberOfRegularAnalyses(self):
        """
        Returns the number of Regular analyses.
        :returns: number of analyses
        :rtype: integer
        """
        return len(self.getRegularAnalyses())

    def getNumberOfQCSamples(self):
        """
        Returns the number of Quality Control samples.
        :returns: number of QC samples
        :rtype: integer
        """
        qc_analyses = self.getQCAnalyses()
        qc_samples = [a.getSample().UID() for a in qc_analyses]
        # discarding any duplicate values
        return len(set(qc_samples))

    def getNumberOfRegularSamples(self):
        """
        Returns the number of regular samples.
        :returns: number of regular samples
        :rtype: integer
        """
        analyses = self.getRegularAnalyses()
        samples = [a.getSample().UID() for a in analyses]
        # discarding any duplicate values
        return len(set(samples))

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

    def setInstrument(self, instrument, override_analyses=False):
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
                    if (not an.getInstrument() or override_analyses)
                        and an.isInstrumentAllowed(instrument)]
        total = 0
        for an in analyses:
            # An analysis can be done using differents Methods.
            # Un method can be supported by more than one Instrument,
            # but not all instruments support one method.
            # We must force to set the instrument's method too. Otherwise,
            # the WS manage results view will display the an's default
            # method and its instruments displaying, only the instruments
            # for the default method in the picklist.
            instr_methods = instrument.getMethods()
            meth = instr_methods[0] if instr_methods else None
            if meth and an.isMethodAllowed(meth):
                if an.getMethod() not in instr_methods:
                    an.setMethod(meth)

            an.setInstrument(instrument)
            total += 1

        self.getField('Instrument').set(self, instrument)
        return total

    def setMethod(self, method, override_analyses=False):
        """ Sets the specified method to the Analyses from the
            Worksheet. Only sets the method if the Analysis
            allows to keep the integrity.
            If an analysis has already been assigned to a method, it won't
            be overriden.
            Returns the number of analyses affected.
        """
        analyses = [an for an in self.getAnalyses()
                    if (not an.getMethod() or
                        not an.getInstrument() or
                        override_analyses) and an.isMethodAllowed(method)]
        total = 0
        for an in analyses:
            success = False
            if an.isMethodAllowed(method):
                success = an.setMethod(method)
            if success is True:
                total += 1

        self.getField('Method').set(self, method)
        return total

    @deprecated('[1703] Orphan. No alternative')
    def getFolderContents(self, contentFilter):
        """
        """
        # The bika_listing machine passes contentFilter to all
        # contentsMethod methods.  We ignore it.
        return list(self.getAnalyses())

    def getAnalystName(self):
        """ Returns the name of the currently assigned analyst
        """
        mtool = getToolByName(self, 'portal_membership')
        analyst = self.getAnalyst().strip()
        analyst_member = mtool.getMemberById(analyst)
        if analyst_member != None:
            return analyst_member.getProperty('fullname')
        return analyst

    def isVerifiable(self):
        """
        Checks it the current Worksheet can be verified. This is, its
        not a cancelled Worksheet and all the analyses that contains
        are verifiable too. Note that verifying a Worksheet is in fact,
        the same as verifying all the analyses that contains. Therefore, the
        'verified' state of a Worksheet shouldn't be a 'real' state,
        rather a kind-of computed state, based on the statuses of the analyses
        it contains. This is why this function checks if the analyses
        contained are verifiable, cause otherwise, the Worksheet will
        never be able to reach a 'verified' state.
        :returns: True or False
        """
        # Check if the worksheet is active
        workflow = getToolByName(self, "portal_workflow")
        objstate = workflow.getInfoFor(self, 'cancellation_state', 'active')
        if objstate == "cancelled":
            return False

        # Check if the worksheet state is to_be_verified
        review_state = workflow.getInfoFor(self, "review_state")
        if review_state == 'to_be_verified':
            # This means that all the analyses from this worksheet have
            # already been transitioned to a 'verified' state, and so the
            # woksheet itself
            return True
        else:
            # Check if the analyses contained in this worksheet are
            # verifiable. Only check those analyses not cancelled and that
            # are not in a kind-of already verified state
            canbeverified = True
            omit = ['published', 'retracted', 'rejected', 'verified']
            for a in self.getAnalyses():
                st = workflow.getInfoFor(a, 'cancellation_state', 'active')
                if st == 'cancelled':
                    continue
                st = workflow.getInfoFor(a, 'review_state')
                if st in omit:
                    continue
                # Can the analysis be verified?
                if not a.isVerifiable(self):
                    canbeverified = False
                    break
            return canbeverified

    def isUserAllowedToVerify(self, member):
        """
        Checks if the specified user has enough privileges to verify the
        current WS. Apart from the roles, this function also checks if the
        current user has enough privileges to verify all the analyses contained
        in this Worksheet. Note that this function only returns if the
        user can verify the worksheet according to his/her privileges
        and the analyses contained (see isVerifiable function)
        :member: user to be tested
        :returns: true or false
        """
        # Check if the user has "Bika: Verify" privileges
        username = member.getUserName()
        allowed = api.user.has_permission(VerifyPermission, username=username)
        if not allowed:
            return False
        # Check if the user is allowed to verify all the contained analyses
        notallowed = [a for a in self.getAnalyses()
                      if not a.isUserAllowedToVerify(member)]
        return not notallowed

    @security.public
    def guard_verify_transition(self):
        return guards.verify(self)

    def getObjectWorkflowStates(self):
        """
        This method is used as a metacolumn.
        Returns a dictionary with the workflow id as key and workflow state as
        value.
        :returns: {'review_state':'active',...}
        :rtype: dict
        """
        workflow = getToolByName(self, 'portal_workflow')
        states = {}
        for w in workflow.getWorkflowsFor(self):
            state = w._getWorkflowStateOf(self).id
            states[w.state_var] = state
        return states

    @security.public
    def workflow_script_submit(self):
        events.after_submit(self)

    @security.public
    def workflow_script_retract(self):
        events.after_retract(self)

    @security.public
    def workflow_script_verify(self):
        events.after_verify(self)

    def workflow_script_reject(self):
        """Copy real analyses to RejectAnalysis, with link to real
           create a new worksheet, with the original analyses, and new
           duplicates and references to match the rejected
           worksheet.
        """
        if skip(self, "reject"):
            return
        utils = getToolByName(self, 'plone_utils')
        workflow = self.portal_workflow

        def copy_src_fields_to_dst(src, dst):
            # These will be ignored when copying field values between analyses
            ignore_fields = ['UID',
                             'id',
                             'title',
                             'allowDiscussion',
                             'subject',
                             'description',
                             'location',
                             'contributors',
                             'creators',
                             'effectiveDate',
                             'expirationDate',
                             'language',
                             'rights',
                             'creation_date',
                             'modification_date',
                             'Layout',    # ws
                             'Analyses',  # ws
            ]
            fields = src.Schema().fields()
            for field in fields:
                fieldname = field.getName()
                if fieldname in ignore_fields:
                    continue
                getter = getattr(src, 'get'+fieldname,
                                 src.Schema().getField(fieldname).getAccessor(src))
                setter = getattr(dst, 'set'+fieldname,
                                 dst.Schema().getField(fieldname).getMutator(dst))
                if getter is None or setter is None:
                    # ComputedField
                    continue
                setter(getter())

        analysis_positions = {}
        for item in self.getLayout():
            analysis_positions[item['analysis_uid']] = item['position']
        old_layout = []
        new_layout = []

        # New worksheet
        worksheets = self.aq_parent
        new_ws = _createObjectByType('Worksheet', worksheets, tmpID())
        new_ws.unmarkCreationFlag()
        new_ws_id = renameAfterCreation(new_ws)
        copy_src_fields_to_dst(self, new_ws)
        new_ws.edit(
            Number = new_ws_id,
            Remarks = self.getRemarks()
        )

        # Objects are being created inside other contexts, but we want their
        # workflow handlers to be aware of which worksheet this is occurring in.
        # We save the worksheet in request['context_uid'].
        # We reset it again below....  be very sure that this is set to the
        # UID of the containing worksheet before invoking any transitions on
        # analyses.
        self.REQUEST['context_uid'] = new_ws.UID()

        # loop all analyses
        analyses = self.getAnalyses()
        new_ws_analyses = []
        old_ws_analyses = []
        for analysis in analyses:
            # Skip published or verified analyses
            review_state = workflow.getInfoFor(analysis, 'review_state', '')
            if review_state in ['published', 'verified', 'retracted']:
                old_ws_analyses.append(analysis.UID())
                old_layout.append({'position': position,
                                   'type':'a',
                                   'analysis_uid':analysis.UID(),
                                   'container_uid':analysis.aq_parent.UID()})
                continue
            # Normal analyses:
            # - Create matching RejectAnalysis inside old WS
            # - Link analysis to new WS in same position
            # - Copy all field values
            # - Clear analysis result, and set Retested flag
            if analysis.portal_type == 'Analysis':
                reject = _createObjectByType('RejectAnalysis', self, tmpID())
                reject.unmarkCreationFlag()
                reject_id = renameAfterCreation(reject)
                copy_src_fields_to_dst(analysis, reject)
                reject.setAnalysis(analysis)
                reject.reindexObject()
                analysis.edit(
                    Result = None,
                    Retested = True,
                )
                analysis.reindexObject()
                position = analysis_positions[analysis.UID()]
                old_ws_analyses.append(reject.UID())
                old_layout.append({'position': position,
                                   'type':'r',
                                   'analysis_uid':reject.UID(),
                                   'container_uid':self.UID()})
                new_ws_analyses.append(analysis.UID())
                new_layout.append({'position': position,
                                   'type':'a',
                                   'analysis_uid':analysis.UID(),
                                   'container_uid':analysis.aq_parent.UID()})
            # Reference analyses
            # - Create a new reference analysis in the new worksheet
            # - Transition the original analysis to 'rejected' state
            if analysis.portal_type == 'ReferenceAnalysis':
                service_uid = analysis.getServiceUID()
                reference = analysis.aq_parent
                reference_type = analysis.getReferenceType()
                new_analysis_uid = reference.addReferenceAnalysis(service_uid,
                                                                  reference_type)
                position = analysis_positions[analysis.UID()]
                old_ws_analyses.append(analysis.UID())
                old_layout.append({'position': position,
                                   'type':reference_type,
                                   'analysis_uid':analysis.UID(),
                                   'container_uid':reference.UID()})
                new_ws_analyses.append(new_analysis_uid)
                new_layout.append({'position': position,
                                   'type':reference_type,
                                   'analysis_uid':new_analysis_uid,
                                   'container_uid':reference.UID()})
                workflow.doActionFor(analysis, 'reject')
                new_reference = reference.uid_catalog(UID=new_analysis_uid)[0].getObject()
                workflow.doActionFor(new_reference, 'assign')
                analysis.reindexObject()
            # Duplicate analyses
            # - Create a new duplicate inside the new worksheet
            # - Transition the original analysis to 'rejected' state
            if analysis.portal_type == 'DuplicateAnalysis':
                src_analysis = analysis.getAnalysis()
                ar = src_analysis.aq_parent
                duplicate_id = new_ws.generateUniqueId('DuplicateAnalysis')
                new_duplicate = _createObjectByType('DuplicateAnalysis',
                                                    new_ws, duplicate_id)
                new_duplicate.unmarkCreationFlag()
                copy_src_fields_to_dst(analysis, new_duplicate)
                workflow.doActionFor(new_duplicate, 'assign')
                new_duplicate.reindexObject()
                position = analysis_positions[analysis.UID()]
                old_ws_analyses.append(analysis.UID())
                old_layout.append({'position': position,
                                   'type':'d',
                                   'analysis_uid':analysis.UID(),
                                   'container_uid':self.UID()})
                new_ws_analyses.append(new_duplicate.UID())
                new_layout.append({'position': position,
                                   'type':'d',
                                   'analysis_uid':new_duplicate.UID(),
                                   'container_uid':new_ws.UID()})
                workflow.doActionFor(analysis, 'reject')
                analysis.reindexObject()

        new_ws.setAnalyses(new_ws_analyses)
        new_ws.setLayout(new_layout)
        new_ws.replaces_rejected_worksheet = self.UID()
        for analysis in new_ws.getAnalyses():
            review_state = workflow.getInfoFor(analysis, 'review_state', '')
            if review_state == 'to_be_verified':
                changeWorkflowState(analysis, "bika_analysis_workflow", "sample_received")
        self.REQUEST['context_uid'] = self.UID()
        self.setLayout(old_layout)
        self.setAnalyses(old_ws_analyses)
        self.replaced_by = new_ws.UID()


    def checkUserManage(self):
        """ Checks if the current user has granted access to this worksheet
            and if has also privileges for managing it.
        """
        granted = False
        can_access = self.checkUserAccess()

        if can_access == True:
            pm = getToolByName(self, 'portal_membership')
            edit_allowed = pm.checkPermission(EditWorksheet, self)
            if edit_allowed:
                # Check if the current user is the WS's current analyst
                member = pm.getAuthenticatedMember()
                analyst = self.getAnalyst().strip()
                if analyst != _c(member.getId()):
                    # Has management privileges?
                    if pm.checkPermission(ManageWorksheets, self):
                        granted = True
                else:
                    granted = True

        return granted

    def checkUserAccess(self):
        """ Checks if the current user has granted access to this worksheet.
            Returns False if the user has no access, otherwise returns True
        """
        # Deny access to foreign analysts
        allowed = True
        pm = getToolByName(self, "portal_membership")
        member = pm.getAuthenticatedMember()

        analyst = self.getAnalyst().strip()
        if analyst != _c(member.getId()):
            roles = member.getRoles()
            restrict = 'Manager' not in roles \
                    and 'LabManager' not in roles \
                    and 'LabClerk' not in roles \
                    and 'RegulatoryInspector' not in roles \
                    and self.bika_setup.getRestrictWorksheetUsersAccess()
            allowed = not restrict

        return allowed

    def setAnalyst(self,analyst):
        for analysis in self.getAnalyses():
            analysis.setAnalyst(analyst)
        self.Schema().getField('Analyst').set(self, analyst)

    def getAnalysesUIDs(self):
        """
        Returns the analyses UIDs from the analyses assigned to this worksheet
        :returns: a list of UIDs
        :rtype: a list of strings
        """
        analyses = self.getAnalyses()
        if isinstance(analyses, list):
            return [an.UID() for an in analyses]
        return []

    def getDepartmentUIDs(self):
        """
        Returns a list of department uids to which the analyses from
        this Worksheet belong to. The list has no duplicates.
        :returns: a list of uids
        :rtype: list
        """
        analyses = self.getAnalyses()
        return list(set([an.getDepartmentUID() for an in analyses]))

registerType(Worksheet, PROJECTNAME)
