# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

import re
import sys

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes.public import (BaseFolder, DisplayList,
                                        ReferenceField, Schema,
                                        SelectionWidget, StringField,
                                        registerType)
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType, safe_unicode
from bika.lims import api, logger
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.fields.remarksfield import RemarksField
from bika.lims.browser.widgets import RemarksWidget
from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.config import PROJECTNAME, WORKSHEET_LAYOUT_OPTIONS
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import (IAnalysisRequest, IDuplicateAnalysis,
                                  IReferenceAnalysis, IReferenceSample,
                                  IRoutineAnalysis, IWorksheet)
from bika.lims.interfaces.analysis import IRequestAnalysis
from bika.lims.permissions import EditWorksheet, ManageWorksheets
from bika.lims.utils import changeWorkflowState, tmpID, to_int
from bika.lims.utils import to_utf8 as _c
from bika.lims.workflow import doActionFor, skip, isTransitionAllowed, \
    ActionHandlerPool, push_reindex_to_actions_pool
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

    RemarksField(
        'Remarks',
        widget=RemarksWidget(
            render_own_label=True,
            label=_("Remarks"),
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

    def addAnalyses(self, analyses):
        """Adds a collection of analyses to the Worksheet at once
        """
        actions_pool = ActionHandlerPool.get_instance()
        actions_pool.queue_pool()
        for analysis in analyses:
            self.addAnalysis(api.get_object(analysis))
        actions_pool.resume()

    def addAnalysis(self, analysis, position=None):
        """- add the analysis to self.Analyses().
           - position is overruled if a slot for this analysis' parent exists
           - if position is None, next available pos is used.
        """
        # Cannot add an analysis if not open, unless a retest
        if api.get_review_status(self) not in ["open", "to_be_verified"]:
            retracted = analysis.getRetestOf()
            if retracted not in self.getAnalyses():
                return

        # Cannot add an analysis that is assigned already
        if analysis.getWorksheet():
            return

        # Just in case
        analyses = self.getAnalyses()
        if analysis in analyses:
            analyses = filter(lambda an: an != analysis, analyses)
            self.setAnalyses(analyses)
            self.updateLayout()

        # Cannot add an analysis if the assign transition is not possible
        # We need to bypass the guard's check for current context!
        api.get_request().set("ws_uid", api.get_uid(self))
        if not isTransitionAllowed(analysis, "assign"):
            return

        # Assign the instrument from the worksheet to the analysis, if possible
        instrument = self.getInstrument()
        if instrument and analysis.isInstrumentAllowed(instrument):
            # TODO Analysis Instrument + Method assignment
            methods = instrument.getMethods()
            if methods:
                # Set the first method assigned to the selected instrument
                analysis.setMethod(methods[0])
            analysis.setInstrument(instrument)
        elif not instrument:
            # If the ws doesn't have an instrument try to set the method
            method = self.getMethod()
            if method and analysis.isMethodAllowed(method):
                analysis.setMethod(method)

        # Assign the worksheet's analyst to the analysis
        # https://github.com/senaite/senaite.core/issues/1409
        analysis.setAnalyst(self.getAnalyst())

        # Transition analysis to "assigned"
        actions_pool = ActionHandlerPool.get_instance()
        actions_pool.queue_pool()
        doActionFor(analysis, "assign")
        self.setAnalyses(analyses + [analysis])
        self.addToLayout(analysis, position)

        # Try to rollback the worksheet to prevent inconsistencies
        doActionFor(self, "rollback_to_open")

        # Reindex Analysis
        push_reindex_to_actions_pool(analysis, idxs=["getWorksheetUID"])

        # Reindex Worksheet
        idxs = ["getAnalysesUIDs"]
        push_reindex_to_actions_pool(self, idxs=idxs)

        # Reindex Analysis Request, if any
        if IRequestAnalysis.providedBy(analysis):
            idxs = ['assigned_state', 'getDueDate']
            push_reindex_to_actions_pool(analysis.getRequest(), idxs=idxs)

        # Resume the actions pool
        actions_pool.resume()

    def removeAnalysis(self, analysis):
        """ Unassigns the analysis passed in from the worksheet.
        Delegates to 'unassign' transition for the analysis passed in
        """
        # We need to bypass the guard's check for current context!
        api.get_request().set("ws_uid", api.get_uid(self))
        if analysis.getWorksheet() == self:
            doActionFor(analysis, "unassign")

    def addToLayout(self, analysis, position=None):
        """ Adds the analysis passed in to the worksheet's layout
        """
        # TODO Redux
        layout = self.getLayout()
        container_uid = self.get_container_for(analysis)
        if IRequestAnalysis.providedBy(analysis) and \
                not IDuplicateAnalysis.providedBy(analysis):
            container_uids = map(lambda slot: slot['container_uid'], layout)
            if container_uid in container_uids:
                position = [int(slot['position']) for slot in layout if
                            slot['container_uid'] == container_uid][0]
            elif not position:
                used_positions = [0, ] + [int(slot['position']) for slot in
                                          layout]
                position = [pos for pos in range(1, max(used_positions) + 2)
                            if pos not in used_positions][0]

        an_type = self.get_analysis_type(analysis)
        self.setLayout(layout + [{'position': position,
                                  'type': an_type,
                                  'container_uid': container_uid,
                                  'analysis_uid': api.get_uid(analysis)}, ])

    def purgeLayout(self):
        """ Purges the layout of not assigned analyses
        """
        uids = map(api.get_uid, self.getAnalyses())
        layout = filter(lambda slot: slot.get("analysis_uid", None) in uids,
                        self.getLayout())
        self.setLayout(layout)

    def _getMethodsVoc(self):
        """
        This function returns the registered methods in the system as a
        vocabulary.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(i.UID, i.Title)
                 for i in bsc(portal_type='Method',
                              is_active=True)]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        items.insert(0, ('', _("Not specified")))
        return DisplayList(list(items))

    def _getInstrumentsVoc(self):
        """
        This function returns the registered instruments in the system as a
        vocabulary. The instruments are filtered by the selected method.
        """
        cfilter = {'portal_type': 'Instrument', 'is_active': True}
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

    def addReferenceAnalyses(self, reference, services, slot=None):
        """ Creates and add reference analyses to the slot by using the
        reference sample and service uids passed in.
        If no destination slot is defined, the most suitable slot will be used,
        typically a new slot at the end of the worksheet will be added.
        :param reference: reference sample to which ref analyses belong
        :param service_uids: he uid of the services to create analyses from
        :param slot: slot where reference analyses must be stored
        :return: the list of reference analyses added
        """
        service_uids = list()
        for service in services:
            if api.is_uid(service):
                service_uids.append(service)
            else:
                service_uids.append(api.get_uid(service))
        service_uids = list(set(service_uids))

        # Cannot add a reference analysis if not open
        if api.get_workflow_status_of(self) != "open":
            return []

        slot_to = to_int(slot)
        if slot_to < 0:
            return []

        if not slot_to:
            # Find the suitable slot to add these references
            slot_to = self.get_suitable_slot_for_reference(reference)
            return self.addReferenceAnalyses(reference, service_uids, slot_to)

        processed = list()
        for analysis in self.get_analyses_at(slot_to):
            if api.get_review_status(analysis) != "retracted":
                service = analysis.getAnalysisService()
                processed.append(api.get_uid(service))
        query = dict(portal_type="AnalysisService", UID=service_uids,
                     sort_on="sortable_title")
        services = filter(lambda service: api.get_uid(service) not in processed,
                          api.search(query, "bika_setup_catalog"))

        # Ref analyses from the same slot must have the same group id
        ref_gid = self.nextRefAnalysesGroupID(reference)
        ref_analyses = list()
        for service in services:
            service_obj = api.get_object(service)
            ref_analysis = self.add_reference_analysis(reference, service_obj,
                                                        slot_to, ref_gid)
            if not ref_analysis:
                continue
            ref_analyses.append(ref_analysis)
        return ref_analyses

    def add_reference_analysis(self, reference, service, slot, ref_gid=None):
        """
        Creates a reference analysis in the destination slot (dest_slot) passed
        in, by using the reference and service_uid. If the analysis
        passed in is not an IReferenceSample or has dependent services, returns
        None. If no reference analyses group id (refgid) is set, the value will
        be generated automatically.
        :param reference: reference sample to create an analysis from
        :param service: the service object to create an analysis from
        :param slot: slot where the reference analysis must be stored
        :param refgid: the reference analyses group id to be set
        :return: the reference analysis or None
        """
        if not reference or not service:
            return None

        if not IReferenceSample.providedBy(reference):
            logger.warning('Cannot create reference analysis from a non '
                           'reference sample: {}'.format(reference.getId()))
            return None

        calc = service.getCalculation()
        if calc and calc.getDependentServices():
            logger.warning('Cannot create reference analyses with dependent'
                           'services: {}'.format(service.getId()))
            return None

        # Create the reference analysis
        ref_analysis = reference.addReferenceAnalysis(service)
        if not ref_analysis:
            logger.warning("Unable to create a reference analysis for "
                           "reference '{0}' and service '{1}'"
                           .format(reference.getId(), service.getKeyword()))
            return None

        # Set ReferenceAnalysesGroupID (same id for the analyses from
        # the same Reference Sample and same Worksheet)
        gid = ref_gid and ref_gid or self.nextRefAnalysesGroupID(reference)
        ref_analysis.setReferenceAnalysesGroupID(gid)

        # Add the reference analysis into the worksheet
        self.setAnalyses(self.getAnalyses() + [ref_analysis, ])
        self.addToLayout(ref_analysis, slot)

        # Reindex
        ref_analysis.reindexObject(idxs=["getAnalyst", "getWorksheetUID",
                                         "getReferenceAnalysesGroupID"])
        self.reindexObject(idxs=["getAnalysesUIDs"])
        return ref_analysis

    def nextRefAnalysesGroupID(self, reference):
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

    def addDuplicateAnalyses(self, src_slot, dest_slot=None):
        """ Creates and add duplicate analyes from the src_slot to the dest_slot
        If no destination slot is defined, the most suitable slot will be used,
        typically a new slot at the end of the worksheet will be added.
        :param src_slot: slot that contains the analyses to duplicate
        :param dest_slot: slot where the duplicate analyses must be stored
        :return: the list of duplicate analyses added
        """
        # Duplicate analyses can only be added if the state of the ws is open
        # unless we are adding a retest
        if api.get_workflow_status_of(self) != "open":
            return []

        slot_from = to_int(src_slot, 0)
        if slot_from < 1:
            return []

        slot_to = to_int(dest_slot, 0)
        if slot_to < 0:
            return []

        if not slot_to:
            # Find the suitable slot to add these duplicates
            slot_to = self.get_suitable_slot_for_duplicate(slot_from)
            return self.addDuplicateAnalyses(src_slot, slot_to)

        processed = map(lambda an: api.get_uid(an.getAnalysis()),
                        self.get_analyses_at(slot_to))
        src_analyses = list()
        for analysis in self.get_analyses_at(slot_from):
            if api.get_uid(analysis) in processed:
                if api.get_workflow_status_of(analysis) != "retracted":
                    continue
            src_analyses.append(analysis)
        ref_gid = None
        duplicates = list()
        for analysis in src_analyses:
            duplicate = self.add_duplicate_analysis(analysis, slot_to, ref_gid)
            if not duplicate:
                continue
            # All duplicates from the same slot must have the same group id
            ref_gid = ref_gid or duplicate.getReferenceAnalysesGroupID()
            duplicates.append(duplicate)
        return duplicates

    def add_duplicate_analysis(self, src_analysis, destination_slot,
                               ref_gid=None):
        """
        Creates a duplicate of the src_analysis passed in. If the analysis
        passed in is not an IRoutineAnalysis, is retracted or has dependent
        services, returns None.If no reference analyses group id (ref_gid) is
        set, the value will be generated automatically.
        :param src_analysis: analysis to create a duplicate from
        :param destination_slot: slot where duplicate analysis must be stored
        :param ref_gid: the reference analysis group id to be set
        :return: the duplicate analysis or None
        """
        if not src_analysis:
            return None

        if not IRoutineAnalysis.providedBy(src_analysis):
            logger.warning('Cannot create duplicate analysis from a non '
                           'routine analysis: {}'.format(src_analysis.getId()))
            return None

        if api.get_review_status(src_analysis) == 'retracted':
            logger.warning('Cannot create duplicate analysis from a retracted'
                           'analysis: {}'.format(src_analysis.getId()))
            return None

        # TODO Workflow - Duplicate Analyses - Consider duplicates with deps
        # Removing this check from here and ensuring that duplicate.getSiblings
        # returns the analyses sorted by priority (duplicates from same
        # AR > routine analyses from same AR > duplicates from same WS >
        # routine analyses from same WS) should be almost enough
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
        if not ref_gid:
            ref_gid = self.nextRefAnalysesGroupID(duplicate.getRequest())
        duplicate.setReferenceAnalysesGroupID(ref_gid)

        # Add the duplicate into the worksheet
        self.addToLayout(duplicate, destination_slot)
        self.setAnalyses(self.getAnalyses() + [duplicate, ])

        # Reindex
        duplicate.reindexObject(idxs=["getAnalyst", "getWorksheetUID",
                                      "getReferenceAnalysesGroupID"])
        self.reindexObject(idxs=["getAnalysesUIDs"])
        return duplicate

    def get_suitable_slot_for_duplicate(self, src_slot):
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
            return -1

        # Are the analyses from src_slot suitable for duplicates creation?
        container = self.get_container_at(slot_from)
        if not container or not IAnalysisRequest.providedBy(container):
            # We cannot create duplicates from analyses other than routine ones,
            # those that belong to an Analysis Request.
            return -1

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

    def get_suitable_slot_for_reference(self, reference):
        """Returns the suitable position for reference analyses, taking into
        account if there is a WorksheetTemplate assigned to this worksheet.

        By default, returns a new slot at the end of the worksheet unless there
        is a slot defined for a reference of the same type (blank or control)
        in the worksheet template's layout that hasn't been used yet.

        :param reference: ReferenceSample the analyses will be created from
        :return: suitable slot position for reference analyses
        """
        if not IReferenceSample.providedBy(reference):
            return -1

        occupied = self.get_slot_positions(type='all') or [0]
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
        uid = api.get_uid(analysis)
        return filter(lambda dup: api.get_uid(dup.getAnalysis()) == uid,
                      self.getDuplicateAnalyses())

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

    def get_analysis_type(self, instance):
        """Returns the string used in slots to differentiate amongst analysis
        types
        """
        if IDuplicateAnalysis.providedBy(instance):
            return 'd'
        elif IReferenceAnalysis.providedBy(instance):
            return instance.getReferenceType()
        elif IRoutineAnalysis.providedBy(instance):
            return 'a'
        return None

    def get_container_for(self, instance):
        """Returns the container id used in slots to group analyses
        """
        if IReferenceAnalysis.providedBy(instance):
            return api.get_uid(instance.getSample())
        return instance.getRequestUID()

    def get_slot_position_for(self, instance):
        """Returns the slot where the instance passed in is located. If not
        found, returns None
        """
        uid = api.get_uid(instance)
        slot = filter(lambda s: s['analysis_uid'] == uid, self.getLayout())
        if not slot:
            return None
        return to_int(slot[0]['position'])

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

    def get_containers_slots(self):
        """Returns a list of tuple (container_uid, slot)
        """
        layout = self.getLayout()
        return map(lambda l: (l["container_uid"], int(l["position"])), layout)

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
        # Get the services from the Worksheet Template
        service_uids = wst.getRawService()
        if not service_uids:
            # No service uids assigned to this Worksheet Template, skip
            logger.warn("Worksheet Template {} has no services assigned"
                        .format(api.get_path(wst)))
            return

        # Search for unassigned analyses
        query = {
            "portal_type": "Analysis",
            "getServiceUID": service_uids,
            "review_state": "unassigned",
            "isSampleReceived": True,
            "is_active": True,
            "sort_on": "getPrioritySortkey"
        }
        analyses = api.search(query, CATALOG_ANALYSIS_LISTING)
        if not analyses:
            return

        # Available slots for routine analyses
        available_slots = self.resolve_available_slots(wst, 'a')
        available_slots.sort(reverse=True)

        # If there is an instrument assigned to this Worksheet Template, take
        # only the analyses that allow this instrument into consideration.
        instrument = wst.getRawInstrument()

        # If there is method assigned to the Worksheet Template, take only the
        # analyses that allow this method into consideration.
        method = wst.getRawRestrictToMethod()

        # Map existing sample uids with slots
        samples_slots = dict(self.get_containers_slots())

        # Keep track of the UIDs of pre-existing Samples
        existing = samples_slots.keys()

        new_analyses = []

        for analysis in analyses:
            analysis = api.get_object(analysis)

            if analysis.getWorksheet():
                # TODO duplicate record or bad value for review_state?
                continue

            if instrument and not analysis.isInstrumentAllowed(instrument):
                # Template's Instrument does not support this analysis
                continue

            if method and not analysis.isMethodAllowed(method):
                # Template's method does not support this analysis
                continue

            # Get the slot where analyses from this sample are located
            sample = analysis.getRequest()
            sample_uid = api.get_uid(sample)
            slot = samples_slots.get(sample_uid)
            if not slot:
                if len(available_slots) == 0:
                    # Maybe next analysis is from a sample with a slot assigned
                    continue

                # Pop next available slot
                slot = available_slots.pop()

            # Keep track of the slot where analyses from this sample must live
            samples_slots[sample_uid] = slot

            # Keep track of the analyses to add
            analysis_info = {
                "analysis": analysis,
                "sample_uid": sample_uid,
                "sample_id": api.get_id(sample),
                "slot": slot,
            }
            new_analyses.append(analysis_info)

        if not new_analyses:
            # No analyses to add
            return

        # No need to sort slots for analyses with a pre-existing sample/slot
        with_samp = filter(lambda a: a["sample_uid"] in existing, new_analyses)
        analyses_slots = map(lambda s: (s["analysis"], s["slot"]), with_samp)

        # Re-sort slots for analyses without a pre-existing sample/slot
        # Analyses retrieved from database are sorted by priority, but we want
        # them to be displayed in natural order in the worksheet
        without_samp = filter(lambda a: a not in with_samp, new_analyses)
        # Sort the items by sample id
        without_samp.sort(key=lambda a: a["sample_id"])
        # Extract the list of analyses (sorted by sample id)
        without_samp_analyses = map(lambda a: a["analysis"], without_samp)
        # Extract the list of assigned slots and sort them in natural order
        without_samp_slots = sorted(map(lambda a: a["slot"], without_samp))
        # Generate the tuple (analysis, slot)
        without_samp_slots = zip(without_samp_analyses, without_samp_slots)
        # Append to those non sorted because of pre-existing slots
        analyses_slots.extend(without_samp_slots)

        # Add the analyses to the worksheet
        map(lambda a: self.addAnalysis(a[0], a[1]), analyses_slots)

        # Reindex the worksheet to update the WorksheetTemplate meta column
        self.reindexObject()

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
            spec_uids = sample.getSupportedServices(only_uids=True)
            return sample, spec_uids

        best_score = [0, 0]
        best_sample = None
        best_supported = None
        for sample in reference_samples:
            specs_uids = sample.getSupportedServices(only_uids=True)
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
                         is_active=True,
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
        samples = [a.getRequestUID() for a in analyses]
        # discarding any duplicate values
        return len(set(samples))

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

    def getAnalystName(self):
        """ Returns the name of the currently assigned analyst
        """
        mtool = getToolByName(self, 'portal_membership')
        analyst = self.getAnalyst().strip()
        analyst_member = mtool.getMemberById(analyst)
        if analyst_member is not None:
            return analyst_member.getProperty('fullname')
        return analyst

    # TODO Workflow - Worksheet - Move to workflow.worksheet.events
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
                new_reference = reference.addReferenceAnalysis(service_uid)
                reference_type = new_reference.getReferenceType()
                new_analysis_uid = api.get_uid(new_reference)
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
                # TODO Workflow - Analysis Retest transition within a Worksheet
                changeWorkflowState(analysis, "bika_analysis_workflow", "assigned")
        self.REQUEST['context_uid'] = self.UID()
        self.setLayout(old_layout)
        self.setAnalyses(old_ws_analyses)
        self.replaced_by = new_ws.UID()

    # TODO Workflow - Worksheet - Remove this function
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

    # TODO Workflow - Worksheet - Remove this function
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
        self.reindexObject()

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

    def getProgressPercentage(self):
        """Returns the progress percentage of this worksheet
        """
        state = api.get_workflow_status_of(self)
        if state == "verified":
            return 100

        steps = 0
        query = dict(getWorksheetUID=api.get_uid(self))
        analyses = api.search(query, CATALOG_ANALYSIS_LISTING)
        max_steps = len(analyses) * 2
        for analysis in analyses:
            an_state = analysis.review_state
            if an_state in ["rejected", "retracted", "cancelled"]:
                steps += 2
            elif an_state in ["verified", "published"]:
                steps += 2
            elif an_state == "to_be_verified":
                steps += 1
        if steps == 0:
            return 0
        if steps > max_steps:
            return 100
        return (steps * 100)/max_steps

registerType(Worksheet, PROJECTNAME)
