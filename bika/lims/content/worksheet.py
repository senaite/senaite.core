# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import re
import sys

from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims import api, deprecated, logger
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.config import PROJECTNAME, WORKSHEET_LAYOUT_OPTIONS
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import (IAnalysisRequest, IDuplicateAnalysis,
                                  IReferenceAnalysis, IReferenceSample,
                                  IRoutineAnalysis, IWorksheet)
from bika.lims.permissions import Verify as VerifyPermission
from bika.lims.permissions import EditWorksheet, ManageWorksheets
from bika.lims.utils import to_utf8 as _c
from bika.lims.utils import changeWorkflowState, tmpID, to_int
from bika.lims.workflow import doActionFor, getCurrentState, skip
from bika.lims.workflow.worksheet import events, guards
from DateTime import DateTime
from plone.api.user import has_permission
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import (BaseFolder, DisplayList,
                                        ReferenceField, Schema,
                                        SelectionWidget, StringField,
                                        TextAreaWidget, TextField,
                                        registerType)
from Products.Archetypes.references import HoldingReference
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATExtensions.ateapi import RecordsField
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType, safe_unicode
from zope.interface import implements


ALL_ANALYSES_TYPES = "all"
ALLOWED_ANALYSES_TYPES = ["a", "b", "c", "d"]


schema = BikaSchema.copy() + Schema((

    UIDReferenceField(
        'WorksheetTemplate',
        allowed_types=('WorksheetTemplate',),
    ),

    RecordsField(
        'Layout',
        required=1,
        subfields=('position', 'type', 'container_uid', 'analysis_uid'),
        subfield_types={'position': 'int'},
    ),

    # all layout info lives in Layout; Analyses is used for back references.
    ReferenceField(
        'Analyses',
        required=1,
        multiValued=1,
        allowed_types=('Analysis', 'DuplicateAnalysis', 'ReferenceAnalysis', 'RejectAnalysis'),
        relationship='WorksheetAnalysis',
    ),

    StringField(
        'Analyst',
        searchable=True,
    ),

    ReferenceField(
        'Method',
        required=0,
        vocabulary_display_path_bound=sys.maxint,
        vocabulary='_getMethodsVoc',
        allowed_types=('Method',),
        relationship='WorksheetMethod',
        referenceClass=HoldingReference,
        widget=SelectionWidget(
            format='select',
            label=_("Method"),
            visible=False,
        ),
    ),

    # TODO Remove. Instruments must be assigned directly to each analysis.
    ReferenceField(
        'Instrument',
        required=0,
        allowed_types=('Instrument',),
        vocabulary='_getInstrumentsVoc',
        relationship='WorksheetInstrument',
        referenceClass=HoldingReference,
    ),

    TextField(
        'Remarks',
        searchable=True,
        default_content_type='text/plain',
        allowed_content_types=('text/plain', ),
        default_output_type="text/plain",
        widget=TextAreaWidget(
            macro="bika_widgets/remarks",
            label=_("Remarks"),
            append_only=True,
        ),
    ),

    StringField(
        'ResultsLayout',
        default='1',
        vocabulary=WORKSHEET_LAYOUT_OPTIONS,
    ),
),
)

schema['id'].required = 0
schema['id'].widget.visible = False
schema['title'].required = 0
schema['title'].widget.visible = {'edit': 'hidden', 'view': 'invisible'}


class Worksheet(BaseFolder, HistoryAwareMixin):
    """A worksheet is a logical group of Analyses accross ARs
    """
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

    def setLayout(self, value):
        """
        Sets the worksheet layout, keeping it sorted by position
        :param value: the layout to set
        """
        new_layout = sorted(value, key=lambda k: k['position'])
        self.getField('Layout').set(self, new_layout)

    security.declareProtected(EditWorksheet, 'addAnalysis')

    def addAnalysis(self, analysis, position=None):
        """- add the analysis to self.Analyses().
           - position is overruled if a slot for this analysis' parent exists
           - if position is None, next available pos is used.
        """
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
        analysis.reindexObject(idxs=['getWorksheetUID', ])

    security.declareProtected(EditWorksheet, 'removeAnalysis')

    def removeAnalysis(self, analysis):
        """ delete an analyses from the worksheet and un-assign it
        """
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

    @deprecated("[1712] Use addReferenceAnalyses instead")
    def addReferences(self, position, reference, service_uids):
        """ Add reference analyses to reference, and add to worksheet layout
        """
        self.addReferenceAnalyses(reference, service_uids, position)

    def addReferenceAnalyses(self, reference, service_uids, dest_slot=None):
        """
        Creates and add reference analyses to the dest_slot by using the
        reference sample and service uids passed in.
        If no destination slot is defined, the most suitable slot will be used,
        typically a new slot at the end of the worksheet will be added.
        :param reference: reference sample to which ref analyses belong
        :param service_uids: he uid of the services to create analyses from
        :param dest_slot: slot where reference aanalyses must be stored
        :return: the list of reference analyses added
        """
        slot_to = to_int(dest_slot)
        if slot_to < 0:
            return

        if not slot_to:
            # Find the suitable slot to add these references
            slot_to = self._get_suitable_slot_for_references(reference)
            if slot_to < 1:
                return

        dest = self.get_analyses_at(slot_to)
        processed = [api.get_uid(an.getAnalysisService()) for an in dest]
        ref_analyses = list()

        # We want the analyses to appear sorted within the slot
        bsc = api.get_tool('bika_setup_catalog')
        services = bsc(portal_type='AnalysisService',
                       UID=service_uids,
                       sort_on='sortable_title')
        refgid = None
        for service in services:
            service_uid = service.UID
            if service_uid in processed:
                continue

            processed.append(service_uid)
            ref_analysis = self._add_reference_analysis(reference,
                                                        service_uid,
                                                        slot_to,
                                                        refgid)

            if ref_analysis:
                # All ref analyses from the same slot must have the same group id
                refgid = ref_analysis.getReferenceAnalysesGroupID()
                ref_analyses.append(ref_analysis)
        return ref_analyses

    def _add_reference_analysis(self, reference, service_uid, dest_slot,
                                refgid=None):
        """
        Creates a reference analysis in the destination slot (dest_slot) passed
        in, by using the reference and service_uid. If the analysis
        passed in is not an IReferenceSample or has dependent services, returns
        None. If no reference analyses group id (refgid) is set, the value will
        be generated automatically.
        :param reference: reference sample to create an analysis from
        :param service_uid: the uid of the service to create an analysis from
        :param dest_slot: slot where the reference analysis must be stored
        :param refgid: the reference analyses group id to be set
        :return: the reference analysis or None
        """
        if not reference or not service_uid:
            return None

        if not IReferenceSample.providedBy(reference):
            logger.warning('Cannot create reference analysis from a non '
                           'reference sample: {}'.format(reference.getId()))
            return None

        uc = api.get_tool('uid_catalog')
        brains = uc(portal_type='AnalysisService', UID=service_uid)
        if not brains:
            logger.warning('No Service found for UID {}'.format(service_uid))
            return None

        service = api.get_object(brains[0])
        calc = service.getCalculation()
        if calc and calc.getDependentServices():
            logger.warning('Cannot create reference analyses with dependent'
                           'services: {}'.format(service.getId()))
            return None

        ref_type = reference.getBlank() and 'b' or 'c'
        ref_uid = reference.addReferenceAnalysis(service_uid, ref_type)
        ref_analysis = uc(UID=ref_uid)[0]
        ref_analysis = api.get_object(ref_analysis)

        # Set ReferenceAnalysesGroupID (same id for the analyses from
        # the same Reference Sample and same Worksheet)
        self._set_referenceanalysis_groupid(ref_analysis, refgid)

        # Set the layout
        layout = self.getLayout()
        ref_pos = {'position': dest_slot,
                   'type': ref_type,
                   'container_uid': api.get_uid(reference),
                   'analysis_uid': ref_uid}
        layout.append(ref_pos)
        self.setLayout(layout)

        # Add the duplicate in the worksheet
        self.setAnalyses(self.getAnalyses() + [ref_analysis, ])
        doActionFor(ref_analysis, 'assign')
        return ref_analysis

    def nextReferenceAnalysesGroupID(self, reference):
        """ Returns the next ReferenceAnalysesGroupID for the given reference
            sample. Gets the last reference analysis registered in the system
            for the specified reference sample and increments in one unit the
            suffix.
        """
        prefix = reference.id + "-"
        if not IReferenceSample.providedBy(reference):
            # Not a ReferenceSample, so this is a duplicate
            prefix = reference.id + "-D"
        bac = getToolByName(reference, 'bika_analysis_catalog')
        ids = bac.Indexes['getReferenceAnalysesGroupID'].uniqueValues()
        rr = re.compile("^" + prefix + "[\d+]+$")
        ids = [int(i.split(prefix)[1]) for i in ids if i and rr.match(i)]
        ids.sort()
        _id = ids[-1] if ids else 0
        suffix = str(_id + 1).zfill(int(3))
        if not IReferenceSample.providedBy(reference):
            # Not a ReferenceSample, so this is a duplicate
            suffix = str(_id + 1).zfill(2)
        return '%s%s' % (prefix, suffix)

    security.declareProtected(EditWorksheet, 'addDuplicateAnalyses')

    def addDuplicateAnalyses(self, src_slot, dest_slot=None):
        """Creates and add duplicate analyes from the src_slot to the dest_slot

        If no destination slot is defined, the most suitable slot will be used,
        typically a new slot at the end of the worksheet will be added.

        :param src_slot: slot that contains the analyses to duplicate
        :param dest_slot: slot where the duplicate analysis must be stored
        :return: the list of duplicate analyses added
        """
        slot_from = to_int(src_slot, 0)
        if slot_from < 1:
            return

        slot_to = to_int(dest_slot, 0)
        if slot_to < 0:
            return

        if not slot_to:
            # Just find the suitable slot to add these duplicates
            slot_to = self._get_suitable_slot_for_duplicate(slot_from)
            if slot_to < 1:
                return

        src_analyses = self.get_analyses_at(slot_from)
        dest_analyses = self.get_analyses_at(slot_to)
        processed = [api.get_uid(an.getAnalysis()) for an in dest_analyses]
        duplicates = list()
        refgid = None
        for analysis in src_analyses:
            analysis_uid = api.get_uid(analysis)
            if analysis_uid in processed:
                continue

            processed.append(analysis_uid)
            duplicate = self._add_duplicate(analysis, slot_to, refgid)

            if duplicate:
                # All duplicates from the same slot must have the same group id
                refgid = duplicate.getReferenceAnalysesGroupID()
                duplicates.append(duplicate)
        return duplicates

    def _add_duplicate(self, src_analysis, destination_slot, refgid=None):
        """
        Creates a duplicate of the src_analysis passed in. If the analysis
        passed in is not an IRoutineAnalysis, is retracted or has dependent
        services, returns None.If no reference analyses group id (refgid) is
        set, the value will be generated automatically.
        :param src_analysis: analysis to create a duplicate from
        :param destination_slot: slot where duplicate analysis must be stored
        :param refgid: the reference analysis group id to be set
        :return: the duplicate analysis or None
        """
        if not src_analysis:
            return None

        if not IRoutineAnalysis.providedBy(src_analysis):
            logger.warning('Cannot create duplicate analysis from a non '
                           'routine analysis: {}'.format(src_analysis.getId()))
            return None

        if getCurrentState(src_analysis) == 'retracted':
            logger.warning('Cannot create duplicate analysis from a retracted'
                           'analysis: {}'.format(src_analysis.getId()))
            return None

        calc = src_analysis.getCalculation()
        if calc and calc.getDependentServices():
            logger.warning('Cannot create duplicate analysis from an'
                           'analysis with dependent services: {}'
                           .format(src_analysis.getId()))
            return None

        # Create the duplicate
        duplicate = _createObjectByType("DuplicateAnalysis", self, tmpID())
        duplicate.setAnalysis(src_analysis)

        # Set ReferenceAnalysesGroupID (same id for the analyses from
        # the same Reference Sample and same Worksheet)
        self._set_referenceanalysis_groupid(duplicate, refgid)

        # Set the layout
        layout = self.getLayout()
        dup_pos = {'position': destination_slot,
                   'type': 'd',
                   'container_uid': duplicate.getRequestID(),
                   'analysis_uid': api.get_uid(duplicate)}
        layout.append(dup_pos)
        self.setLayout(layout)

        # Add the duplicate in the worksheet
        self.setAnalyses(self.getAnalyses() + [duplicate, ])
        doActionFor(duplicate, 'assign')

        return duplicate

    def _set_referenceanalysis_groupid(self, analysis, refgid=None):
        """
        Inferes and store the reference analysis group id to the analysis passed
        in. If the analysis passed in is neither a reference analysis nor a
        duplicate, does nothing. If no reference analyses group id (refgid) is
        set, the value will be generated automatically.
        Reference analysis group id is used to differentiate multiple reference
        analyses for the same sample/analysis within a worksheet.
        :param analysis: analysis to set the reference analysis group id
        :param refgid: the reference analyses group id to be used
        """
        if not analysis:
            return

        is_duplicate = IDuplicateAnalysis.providedBy(analysis)
        is_reference = IReferenceAnalysis.providedBy(analysis)
        if not is_duplicate and not is_reference:
            logger.warn('Cannot set a reference analysis group id to an '
                        'analysis that is neither a reference analysis nor '
                        'a duplicate: {}'.format(analysis.getId()))
            return

        sample = analysis.getSample()
        if not refgid:
            refgid = self.nextReferenceAnalysesGroupID(sample)
        analysis.setReferenceAnalysesGroupID(refgid)
        analysis.reindexObject(idxs=["getReferenceAnalysesGroupID"])

    def _get_suitable_slot_for_duplicate(self, src_slot):
        """Returns the suitable position for a duplicate analysis, taking into
        account if there is a WorksheetTemplate assigned to this worksheet.

        By default, returns a new slot at the end of the worksheet unless there
        is a slot defined for a duplicate of the src_slot in the worksheet
        template layout not yet used.

        :param src_slot:
        :return: suitable slot position for a duplicate of src_slot
        """
        slot_from = to_int(src_slot, 0)
        if slot_from < 1:
            return 0

        # Are the analyses from src_slot suitable for duplicates creation?
        container = self.get_container_at(slot_from)
        if not container or not IAnalysisRequest.providedBy(container):
            # We cannot create duplicates from analyses other than routine ones,
            # those that belong to an Analysis Request.
            return 0

        occupied = self.get_slot_positions(type='all')
        wst = self.getWorksheetTemplate()
        if not wst:
            # No worksheet template assigned, add a new slot at the end of
            # the worksheet with the duplicate there
            slot_to = max(occupied) + 1
            return slot_to

        # If there is a match with the layout defined in the Worksheet
        # Template, use that slot instead of adding a new one at the end of
        # the worksheet
        layout = wst.getLayout()
        for pos in layout:
            if pos['type'] != 'd' or to_int(pos['dup']) != slot_from:
                continue
            slot_to = int(pos['pos'])
            if slot_to in occupied:
                # Not an empty slot
                continue

            # This slot is empty, use it instead of adding a new
            # slot at the end of the worksheet
            return slot_to

        # Add a new slot at the end of the worksheet, but take into account
        # that a worksheet template is assigned, so we need to take care to
        # not override slots defined by its layout
        occupied.append(len(layout))
        slot_to = max(occupied) + 1
        return slot_to

    def _get_suitable_slot_for_references(self, reference):
        """Returns the suitable position for reference analyses, taking into
        account if there is a WorksheetTemplate assigned to this worksheet.

        By default, returns a new slot at the end of the worksheet unless there
        is a slot defined for a reference of the same type (blank or control)
        in the worksheet template's layout that hasn't been used yet template
        layout not yet used.

        :param reference: ReferenceSample the analyses will be created from
        :return: suitable slot position for reference analyses
        """
        if not IReferenceSample.providedBy(reference):
            return 0

        occupied = self.get_slot_positions(type='all')
        wst = self.getWorksheetTemplate()
        if not wst:
            # No worksheet template assigned, add a new slot at the end of the
            # worksheet with the reference analyses there
            slot_to = max(occupied) + 1
            return slot_to

        # If there is a match with the layout defined in the Worksheet Template,
        # use that slot instead of adding a new one at the end of the worksheet
        slot_type = reference.getBlank() and 'b' or 'c'
        layout = wst.getLayout()

        for pos in layout:
            if pos['type'] != slot_type:
                continue
            slot_to = int(pos['pos'])
            if slot_to in occupied:
                # Not an empty slot
                continue

            # This slot is empty, use it instead of adding a new slot at the end
            # of the worksheet
            return slot_to

        # Add a new slot at the end of the worksheet, but take into account
        # that a worksheet template is assigned, so we need to take care to
        # not override slots defined by its layout
        occupied.append(len(layout))
        slot_to = max(occupied) + 1
        return slot_to

    def get_duplicates_for(self, analysis):
        """Returns the duplicates from the current worksheet that were created
        by using the analysis passed in as the source

        :param analysis: routine analyses used as the source for the duplicates
        :return: a list of duplicates generated from the analysis passed in
        """
        if not analysis:
            return list()
        analysis_uid = api.get_uid(analysis)
        matches = list()
        duplicates = self.getDuplicates()

        for duplicate in duplicates:
            dup_analysis = duplicate.getAnalysis()
            dup_analysis_uid = api.get_uid(dup_analysis)
            if dup_analysis_uid != analysis_uid:
                continue
            matches.append(dup_analysis)

        return matches

    def get_analyses_at(self, slot):
        """Returns the list of analyses assigned to the slot passed in, sorted by
        the positions they have within the slot.

        :param slot: the slot where the analyses are located
        :type slot: int
        :return: a list of analyses
        """

        # ensure we have an integer
        slot = to_int(slot)

        if slot < 1:
            return list()

        analyses = list()
        layout = self.getLayout()

        for pos in layout:
            layout_slot = to_int(pos['position'])
            uid = pos['analysis_uid']
            if layout_slot != slot or not uid:
                continue
            analyses.append(api.get_object_by_uid(uid))

        return analyses

    def get_container_at(self, slot):
        """Returns the container object assigned to the slot passed in

        :param slot: the slot where the analyses are located
        :type slot: int
        :return: the container (analysis request, reference sample, etc.)
        """

        # ensure we have an integer
        slot = to_int(slot)

        if slot < 1:
            return None

        layout = self.getLayout()

        for pos in layout:
            layout_slot = to_int(pos['position'])
            uid = pos['container_uid']
            if layout_slot != slot or not uid:
                continue
            return api.get_object_by_uid(uid)

        return None

    def get_slot_positions(self, type='a'):
        """Returns a list with the slots occupied for the type passed in.

        Allowed type of analyses are:

            'a'   (routine analysis)
            'b'   (blank analysis)
            'c'   (control)
            'd'   (duplicate)
            'all' (all analyses)

        :param type: type of the analysis
        :return: list of slot positions
        """
        if type not in ALLOWED_ANALYSES_TYPES and type != ALL_ANALYSES_TYPES:
            return list()

        layout = self.getLayout()
        slots = list()

        for pos in layout:
            if type != ALL_ANALYSES_TYPES and pos['type'] != type:
                continue
            slots.append(to_int(pos['position']))

        # return a unique list of sorted slot positions
        return sorted(set(slots))

    def get_slot_position(self, container, type='a'):
        """Returns the slot where the analyses from the type and container passed
        in are located within the worksheet.

        :param container: the container in which the analyses are grouped
        :param type: type of the analysis
        :return: the slot position
        :rtype: int
        """
        if not container or type not in ALLOWED_ANALYSES_TYPES:
            return None
        uid = api.get_uid(container)
        layout = self.getLayout()

        for pos in layout:
            if pos['type'] != type or pos['container_uid'] != uid:
                continue
            return to_int(pos['position'])
        return None

    def resolve_available_slots(self, worksheet_template, type='a'):
        """Returns the available slots from the current worksheet that fits
        with the layout defined in the worksheet_template and type of analysis
        passed in.

        Allowed type of analyses are:

            'a' (routine analysis)
            'b' (blank analysis)
            'c' (control)
            'd' (duplicate)

        :param worksheet_template: the worksheet template to match against
        :param type: type of analyses to restrict that suit with the slots
        :return: a list of slots positions
        """
        if not worksheet_template or type not in ALLOWED_ANALYSES_TYPES:
            return list()

        ws_slots = self.get_slot_positions(type)
        layout = worksheet_template.getLayout()
        slots = list()

        for row in layout:
            # skip rows that do not match with the given type
            if row['type'] != type:
                continue

            slot = to_int(row['pos'])

            if slot in ws_slots:
                # We only want those that are empty
                continue

            slots.append(slot)
        return slots

    def _apply_worksheet_template_routine_analyses(self, wst):
        """Add routine analyses to worksheet according to the worksheet template
        layout passed in w/o overwriting slots that are already filled.

        If the template passed in has an instrument assigned, only those
        routine analyses that allows the instrument will be added.

        If the template passed in has a method assigned, only those routine
        analyses that allows the method will be added

        :param wst: worksheet template used as the layout
        :returns: None
        """
        bac = api.get_tool("bika_analysis_catalog")
        services = wst.getService()
        wst_service_uids = [s.UID() for s in services]

        query = {
            "portal_type": "Analysis",
            "getServiceUID": wst_service_uids,
            "review_state": "sample_received",
            "worksheetanalysis_review_state": "unassigned",
            "cancellation_state": "active",
            "sort_on": "getPrioritySortkey"
        }

        analyses = bac(query)

        # No analyses, nothing to do
        if not analyses:
            return

        # Available slots for routine analyses. Sort reverse, cause we need a
        # stack for sequential assignment of slots
        available_slots = self.resolve_available_slots(wst, 'a')
        available_slots.sort(reverse=True)

        # If there is an instrument assigned to this Worksheet Template, take
        # only the analyses that allow this instrument into consideration.
        instrument = wst.getInstrument()

        # If there is method assigned to the Worksheet Template, take only the
        # analyses that allow this method into consideration.
        method = wst.getRestrictToMethod()

        # This worksheet is empty?
        num_routine_analyses = len(self.getRegularAnalyses())

        # Group Analyses by Analysis Requests
        ar_analyses = dict()
        ar_slots = dict()
        ar_fixed_slots = dict()

        for brain in analyses:
            obj = api.get_object(brain)
            arid = obj.getRequestID()

            if instrument and not obj.isInstrumentAllowed(instrument):
                # Exclude those analyses for which the worksheet's template
                # instrument is not allowed
                continue

            if method and not obj.isMethodAllowed(method):
                # Exclude those analyses for which the worksheet's template
                # method is not allowed
                continue

            slot = ar_slots.get(arid, None)
            if not slot:
                # We haven't processed other analyses that belong to the same
                # Analysis Request as the current one.
                if len(available_slots) == 0 and num_routine_analyses == 0:
                    # No more slots available for this worksheet/template, so
                    # we cannot add more analyses to this WS. Also, there is no
                    # chance to process a new analysis with an available slot.
                    break

                if num_routine_analyses == 0:
                    # This worksheet is empty, but there are slots still
                    # available, assign the next available slot to this analysis
                    slot = available_slots.pop()
                else:
                    # This worksheet is not empty and there are slots still
                    # available.
                    slot = self.get_slot_position(obj.getRequest())
                    if slot:
                        # Prefixed slot position
                        ar_fixed_slots[arid] = slot
                        if arid not in ar_analyses:
                            ar_analyses[arid] = list()
                        ar_analyses[arid].append(obj)
                        continue

                    # This worksheet does not contain any other analysis
                    # belonging to the same Analysis Request as the current
                    if len(available_slots) == 0:
                        # There is the chance to process a new analysis that
                        # belongs to an Analysis Request that is already
                        # in this worksheet.
                        continue

                    # Assign the next available slot
                    slot = available_slots.pop()

            ar_slots[arid] = slot
            if arid not in ar_analyses:
                ar_analyses[arid] = list()
            ar_analyses[arid].append(obj)

        # Sort the analysis requests by sortable_title, so the ARs will appear
        # sorted in natural order. Since we will add the analysis with the
        # exact slot where they have to be displayed, we need to sort the slots
        # too and assign them to each group of analyses in natural order
        sorted_ar_ids = sorted(ar_analyses.keys())
        slots = sorted(ar_slots.values(), reverse=True)

        # Add regular analyses
        for ar_id in sorted_ar_ids:
            slot = ar_fixed_slots.get(ar_id, None)
            if not slot:
                slot = slots.pop()
            ar_ans = ar_analyses[ar_id]
            for ar_an in ar_ans:
                self.addAnalysis(ar_an, slot)

    def _apply_worksheet_template_duplicate_analyses(self, wst):
        """Add duplicate analyses to worksheet according to the worksheet template
        layout passed in w/o overwrite slots that are already filled.

        If the slot where the duplicate must be located is available, but the
        slot where the routine analysis should be found is empty, no duplicate
        will be generated for that given slot.

        :param wst: worksheet template used as the layout
        :returns: None
        """
        wst_layout = wst.getLayout()

        for row in wst_layout:
            if row['type'] != 'd':
                continue

            src_pos = to_int(row['dup'])
            dest_pos = to_int(row['pos'])

            self.addDuplicateAnalyses(src_pos, dest_pos)

    def _resolve_reference_sample(self, reference_samples=None,
                                  service_uids=None):
        """Returns the reference sample from reference_samples passed in that fits
        better with the service uid requirements. This is, the reference sample
        that covers most (or all) of the service uids passed in and has less
        number of remaining service_uids.

        If no reference_samples are set, returns None

        If no service_uids are set, returns the first reference_sample

        :param reference_samples: list of reference samples
        :param service_uids: list of service uids
        :return: the reference sample that fits better with the service uids
        """
        if not reference_samples:
            return None, list()

        if not service_uids:
            # Since no service filtering has been defined, there is no need to
            # look for the best choice. Return the first one
            sample = reference_samples[0]
            spec_uids = sample.getResultsRangeDict().keys()
            return sample, spec_uids

        best_score = [0, 0]
        best_sample = None
        best_supported = None
        for sample in reference_samples:
            specs_uids = sample.getResultsRangeDict().keys()
            supported = [uid for uid in specs_uids if uid in service_uids]
            matches = len(supported)
            overlays = len(service_uids) - matches
            overlays = 0 if overlays < 0 else overlays

            if overlays == 0 and matches == len(service_uids):
                # Perfect match.. no need to go further
                return sample, supported

            if not best_sample \
                    or matches > best_score[0] \
                    or (matches == best_score[0] and overlays < best_score[1]):
                best_sample = sample
                best_score = [matches, overlays]
                best_supported = supported

        return best_sample, best_supported

    def _resolve_reference_samples(self, wst, type):
        """
        Resolves the slots and reference samples in accordance with the
        Worksheet Template passed in and the type passed in.
        Returns a list of dictionaries
        :param wst: Worksheet Template that defines the layout
        :param type: type of analyses ('b' for blanks, 'c' for controls)
        :return: list of dictionaries
        """
        if not type or type not in ['b', 'c']:
            return []

        bc = api.get_tool("bika_catalog")
        wst_type = type == 'b' and 'blank_ref' or 'control_ref'

        slots_sample = list()
        available_slots = self.resolve_available_slots(wst, type)
        wst_layout = wst.getLayout()
        for row in wst_layout:
            slot = int(row['pos'])
            if slot not in available_slots:
                continue

            ref_definition_uid = row.get(wst_type, None)
            if not ref_definition_uid:
                # Only reference analyses with reference definition can be used
                # in worksheet templates
                continue

            samples = bc(portal_type='ReferenceSample',
                         review_state='current',
                         inactive_state='active',
                         getReferenceDefinitionUID=ref_definition_uid)

            # We only want the reference samples that fit better with the type
            # and with the analyses defined in the Template
            services = wst.getService()
            services = [s.UID() for s in services]
            candidates = list()
            for sample in samples:
                obj = api.get_object(sample)
                if (type == 'b' and obj.getBlank()) or \
                        (type == 'c' and not obj.getBlank()):
                    candidates.append(obj)

            sample, uids = self._resolve_reference_sample(candidates, services)
            if not sample:
                continue

            slots_sample.append({'slot': slot,
                                 'sample': sample,
                                 'supported_services': uids})

        return slots_sample

    def _apply_worksheet_template_reference_analyses(self, wst, type='all'):
        """
        Add reference analyses to worksheet according to the worksheet template
        layout passed in. Does not overwrite slots that are already filled.
        :param wst: worksheet template used as the layout
        """
        if type == 'all':
            self._apply_worksheet_template_reference_analyses(wst, 'b')
            self._apply_worksheet_template_reference_analyses(wst, 'c')
            return

        if type not in ['b', 'c']:
            return

        references = self._resolve_reference_samples(wst, type)
        for reference in references:
            slot = reference['slot']
            sample = reference['sample']
            services = reference['supported_services']
            self.addReferenceAnalyses(sample, services, slot)

    def applyWorksheetTemplate(self, wst):
        """ Add analyses to worksheet according to wst's layout.
            Will not overwrite slots which are filled already.
            If the selected template has an instrument assigned, it will
            only be applied to those analyses for which the instrument
            is allowed, the same happens with methods.
        """
        # Store the Worksheet Template field
        self.getField('WorksheetTemplate').set(self, wst)

        if not wst:
            return

        # Apply the template for routine analyses
        self._apply_worksheet_template_routine_analyses(wst)

        # Apply the template for duplicate analyses
        self._apply_worksheet_template_duplicate_analyses(wst)

        # Apply the template for reference analyses (blanks and controls)
        self._apply_worksheet_template_reference_analyses(wst)

        # Assign the instrument
        instrument = wst.getInstrument()
        if instrument:
            self.setInstrument(instrument, True)

        # Assign the method
        method = wst.getRestrictToMethod()
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
                    if (not an.getInstrument() or override_analyses) and
                    an.isInstrumentAllowed(instrument)]
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
        if analyst_member is not None:
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
        allowed = has_permission(VerifyPermission, username=username)
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
        workflow = self.portal_workflow

        def copy_src_fields_to_dst(src, dst):
            # These will be ignored when copying field values between analyses
            ignore_fields = [
                'UID',
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
                getter = getattr(src, 'get' + fieldname,
                                 src.Schema().getField(fieldname).getAccessor(src))
                setter = getattr(dst, 'set' + fieldname,
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
            Number=new_ws_id,
            Remarks=self.getRemarks()
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

                # XXX where does position come from?
                old_layout.append({'position': position,
                                   'type': 'a',
                                   'analysis_uid': analysis.UID(),
                                   'container_uid': analysis.aq_parent.UID()})
                continue
            # Normal analyses:
            # - Create matching RejectAnalysis inside old WS
            # - Link analysis to new WS in same position
            # - Copy all field values
            # - Clear analysis result, and set Retested flag
            if analysis.portal_type == 'Analysis':
                reject = _createObjectByType('RejectAnalysis', self, tmpID())
                reject.unmarkCreationFlag()
                copy_src_fields_to_dst(analysis, reject)
                reject.setAnalysis(analysis)
                reject.reindexObject()
                analysis.edit(
                    Result=None,
                    Retested=True,
                )
                analysis.reindexObject()
                position = analysis_positions[analysis.UID()]
                old_ws_analyses.append(reject.UID())
                old_layout.append({'position': position,
                                   'type': 'r',
                                   'analysis_uid': reject.UID(),
                                   'container_uid': self.UID()})
                new_ws_analyses.append(analysis.UID())
                new_layout.append({'position': position,
                                   'type': 'a',
                                   'analysis_uid': analysis.UID(),
                                   'container_uid': analysis.aq_parent.UID()})
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
                                   'type': reference_type,
                                   'analysis_uid': analysis.UID(),
                                   'container_uid': reference.UID()})
                new_ws_analyses.append(new_analysis_uid)
                new_layout.append({'position': position,
                                   'type': reference_type,
                                   'analysis_uid': new_analysis_uid,
                                   'container_uid': reference.UID()})
                workflow.doActionFor(analysis, 'reject')
                new_reference = reference.uid_catalog(UID=new_analysis_uid)[0].getObject()
                workflow.doActionFor(new_reference, 'assign')
                analysis.reindexObject()
            # Duplicate analyses
            # - Create a new duplicate inside the new worksheet
            # - Transition the original analysis to 'rejected' state
            if analysis.portal_type == 'DuplicateAnalysis':
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
                                   'type': 'd',
                                   'analysis_uid': analysis.UID(),
                                   'container_uid': self.UID()})
                new_ws_analyses.append(new_duplicate.UID())
                new_layout.append({'position': position,
                                   'type': 'd',
                                   'analysis_uid': new_duplicate.UID(),
                                   'container_uid': new_ws.UID()})
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

        if can_access is True:
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

    def setAnalyst(self, analyst):
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
