# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from operator import itemgetter

from bika.lims import bikaMessageFactory as _, logger, api
from bika.lims.browser.analyses import AnalysesView as BaseView
from bika.lims.utils import to_int


class AnalysesView(BaseView):
    """ This renders the table for ManageResultsView.
    """
    def __init__(self, context, request):
        BaseView.__init__(self, context, request)
        self.context = context
        self.request = request
        self.analyst = None
        self.instrument = None
        self.contentFilter = {
            'getWorksheetUID': context.UID(),
            'sort_on': 'sortable_title'
        }
        self.sort_on = 'sortable_title'
        self.icon = self.portal_url + "/++resource++bika.lims.images/worksheet_big.png"
        self.allow_edit = True
        self.show_categories = False
        self.expand_all_categories = False
        self.columns = {
            'Pos': {'title': _('Position')},
            'DueDate': {'title': _('Due Date')},
            'Service': {'title': _('Analysis')},
            'Method': {'title': _('Method')},
            'DetectionLimit': {
                'title': _('DL'),
                'sortable': False,
                'toggle': False},
            'Result': {'title': _('Result'),
                       'input_width': '6',
                       'input_class': 'ajax_calculate numeric',
                       'sortable': False},
            'Uncertainty': {'title': _('+-')},
            'ResultDM': {'title': _('Dry')},
            'retested': {'title': "<img src='++resource++bika.lims.images/retested.png' title='%s'/>" % _('Retested'),
                         'type':'boolean'},
            'Attachments': {'title': _('Attachments')},
            'Instrument': {'title': _('Instrument')},
            'state_title': {'title': _('State')},
        }
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'transitions': [{'id':'submit'},
                             {'id':'verify'},
                             {'id':'retract'},
                             {'id':'unassign'}],
             'columns':['Pos',
                        'Service',
                        'Method',
                        'Instrument',
                        'DetectionLimit',
                        'Result',
                        'Uncertainty',
                        'DueDate',
                        'state_title',
                        'Attachments']
             },
        ]
        self.bika_setup = api.get_bika_setup()
        self.uids_strpositions = self.get_uids_strpositions()
        self.items_rowspans = dict()

    def isItemAllowed(self, obj):
        """
        Returns true if the current analysis to be rendered has a slot assigned
        for the current layout.
        :param obj: analysis to be rendered as a row in the list
        :type obj: ATContentType/DexterityContentType
        :return: True if the obj has an slot assigned. Otherwise, False.
        :rtype: bool
        """
        uid = api.get_uid(obj)
        if not self.get_item_slot(uid):
            logger.warning("Slot not assigned to item %s" % uid)
            return False
        return BaseView.isItemAllowed(self, obj)

    def folderitem(self, obj, item, index):
        """
        Applies new properties to the item (analysis) that is currently being
        rendered as a row in the list.
        :param obj: analysis to be rendered as a row in the list
        :param item: dict representation of the analysis, suitable for the list
        :param index: current position of the item within the list
        :type obj: ATContentType/DexterityContentType
        :type item: dict
        :type index: int
        :return: the dict representation of the item
        :rtype: dict
        """
        item = BaseView.folderitem(self, obj, item, index)
        item_obj = api.get_object(obj)
        uid = item['uid']

        # Slot is the row position where all analyses sharing the same parent
        # (eg. AnalysisRequest, SampleReference), will be displayed as a group
        slot = self.get_item_slot(uid)
        item['Pos'] = slot

        # The position string contains both the slot + the position of the
        # analysis within the slot: "position_sortkey" will be used to sort all
        # the analyses to be displayed in the list
        str_position = self.uids_strpositions[uid]
        item['pos_sortkey'] = str_position

        item['colspan'] = {'Pos':1}
        item['Service'] = item_obj.Title()
        item['Category'] = item_obj.getCategoryTitle()
        item['DueDate'] = self.ulocalized_time(item_obj, long_format=0)
        item['class']['Service'] = 'service_title'

        # To prevent extra loops, we compute here the number of analyses to be
        # rendered within each slot. This information will be useful later for
        # applying rowspan to the first cell of each slot, that contains info
        # about the parent of all the analyses contained in that slot (e.g
        # Analysis Request ID, Sample Type, etc.)
        rowspans = self.items_rowspans.get(slot, 0) + 1
        remarks = item.get('Remarks', None)
        remarks_edit = 'Remarks' in item.get('allow_edit', [])
        remarks_enabled = self.bika_setup.getEnableAnalysisRemarks()
        if remarks_enabled and (remarks or remarks_edit):
            # Increase in one unit the rowspan, cause the comment field for
            # this analysis will be rendered in a new row, below the row that
            # displays the current item
            rowspans += 1
        # We map this rowspan information in items_rowspan, that will be used
        # later during the rendereing of slot headers (first cell of each row)
        self.items_rowspans[slot] = rowspans

        return item

    def folderitems(self):
        """
        Returns an array of dictionaries, each dictionary represents an analysis
        row to be rendered in the list. The array returned is sorted in
        accordance with the layout positions set for the analyses this worksheet
        contains when the analyses were added in the worksheet.
        :returns: list of dicts with the items to be rendered in the list
        """
        items = BaseView.folderitems(self)

        # Fill empty positions from the layout with fake rows. The worksheet
        # can be generated by making use of a WorksheetTemplate, so there is the
        # chance that some slots of this worksheet being empty. We need to
        # render a row still, at lest to display the slot number (Pos)
        self.fill_empty_slots(items)

        # Sort the items in accordance with the layout
        items = sorted(items, key=itemgetter('pos_sortkey'))

        # Fill the slot header cells (first cell of each row). Each slot
        # contains the analyses that belong to the same parent (AnalysisRequest,
        # ReferenceSample), so the information about the parent must be
        # displayed in the first cell of each slot.
        self.fill_slots_headers(items)

        return items

    def get_uids_strpositions(self):
        """
        Returns a dict with the positions of each analysis within the current
        worksheet in accordance with the current layout. The key of the dict is
        the uid of the analysis and the value is an string representation of the
        full position of the analysis within the list:
            {<analysis_uid>: '<slot_number>:<position_within_slot>',}
        :return: a dictionary with the full position within the worksheet of
            all analyses defined in the current layout.
        """
        uids_positions = dict()
        layout = self.context.getLayout()
        layout = layout and layout or []
        # Map the analysis uids with their positions.
        occupied = []
        next_positions = {}
        for item in layout:
            uid = item.get('analysis_uid', '')
            slot = int(item['position'])
            occupied.append(slot)
            position = next_positions.get(slot, 1)
            str_position = "{:010}:{:010}".format(slot, position)
            next_positions[slot] = position + 1
            uids_positions[uid] = str_position

        # Fill empties
        last_slot = max(occupied) if occupied else 1
        empties = [num for num in range(1, last_slot) if num not in occupied]
        for empty_slot in empties:
            str_position = "{:010}:{:010}".format(empty_slot, 1)
            uid = "empty-{}".format(empty_slot)
            uids_positions[uid] = str_position

        return uids_positions

    def get_item_position(self, analysis_uid):
        """
        Returns a list with the position for the analysis_uid passed in within
        the current worksheet in accordance with the current layout, where
        the first item from the list returned is the slot and the second is
        the position of the analysis within the slot.
        :param analysis_uid: uid of the analysis the position is requested
        :return: the position (slot + position within slot) of the analysis
        :rtype: list
        """
        str_position = self.uids_strpositions.get(analysis_uid, '')
        tokens = str_position.split(':')
        if len(tokens) != 2:
            return None
        return [to_int(tokens[0]), to_int(tokens[1])]

    def get_item_slot(self, analysis_uid):
        """
        Returns the slot number where the analysis must be rendered.
        An slot contains all analyses that belong to the same parent
        (AnalysisRequest, ReferenceSample).
        :param analysis_uid: the uid of the analysis the slot is requested
        :return: the slot number where the analysis must be rendered
        """
        position = self.get_item_position(analysis_uid)
        if not position:
            return None
        return position[0]

    def _get_slots(self, empty_uid=False):
        """
        Returns a list with the position number of the slots that are occupied
        (if empty_uid=False) or are empty (if empty_uid=True)
        :param empty_uid: True exclude occupied slots. False excludes empties
        :return: sorted list with slot numbers
        """
        slots = list()
        for uid, position in self.uids_strpositions.items():
            if empty_uid and not uid.startswith('empty-'):
                continue
            elif not empty_uid and uid.startswith('empty-'):
                continue
            tokens = position.split(':')
            slots.append(to_int(tokens[0]))
        return sorted(list(set(slots)))

    def get_occupied_slots(self):
        """
        Returns the list of occupied slots, those that have at least one
        analysis assigned according to the current layout.
        Delegates to self._get_slots(empty_uid=False)
        :return: list of slot numbers that at least have one analysis assigned
        """
        return self._get_slots(empty_uid=False)

    def get_empty_slots(self):
        """
        Returns the list of empty slots, those that don't have any analysis
        assigned according to the current layout.
        Delegates to self._get_slots(empty_uid=True)
        :return: list of slot numbers that don't have any analysis assigned
        """
        return self._get_slots(empty_uid=True)

    def fill_empty_slots(self, items):
        """
        Append dicts to the items passed in for those slots that don't have any
        analysis assigned but the row needs to be rendered still.
        :param items: dictionary with the items to be rendered in the list
        """
        for pos in self.get_empty_slots():
            colspan = len(self.columns) + len(self.interim_fields)
            item = {
                'obj': self.context,
                'id': self.context.id,
                'uid': self.context.UID(),
                'title': self.context.Title(),
                'type_class': 'blank-worksheet-row',
                'url': self.context.absolute_url(),
                'relative_url': self.context.absolute_url(),
                'view_url': self.context.absolute_url(),
                'path': "/".join(self.context.getPhysicalPath()),
                'before': {},
                'after': {},
                'choices': {},
                'class': {},
                'state_class': 'state-empty',
                'allow_edit': [],
                'colspan': {'Pos': colspan},
                'rowspan': {'Pos': 1},
                'Pos': pos,
                'pos_sortkey': "{:010}:{:010}".format(pos, 1),
                'Service': '',
                'Attachments': '',
                'state_title': 's',}

            item['replace'] = {
                'Pos': "<table width='100%' cellpadding='0' cellspacing='0'>" + \
                       "<tr><td class='pos'>%s</td>" % pos + \
                       "<td align='right'>&nbsp;</td></tr></table>",
                'select_column': '',
            }

            items.append(item)

    def fill_slots_headers(self, items):
        """
        Generates the header cell for each slot.
        For each slot, the first cell displays information about the parent all
        analyses within that given slot have in common, such as the AR Id,
        SampleType, etc.
        :param items: dictionary with items to be rendered in the list
        """
        prev_position = 0
        for item in items:
            item_position = item['Pos']
            if item_position == prev_position:
                # We've already filled the head cell for this slot
                continue
            if item['state_title'] == 's':
                # This is an empty slot
                continue

            # This is the first analysis found for the given position, add the
            # slot info in there and apply a rowspan accordingly.
            rowspan = self.items_rowspans.get(item_position, 1)
            prev_position = item_position
            item['rowspan'] = {'Pos': rowspan}
            item['replace']['Pos'] = self.get_slot_header(item)

    def get_slot_header(self, item):
        """
        Generates a slot header (the first cell of the row) for the item
        :param item: the item for which the slot header is requested
        :return: the html contents to be displayed in the first cell of a slot
        """
        obj = item['obj']
        obj = api.get_object(obj)

        # TODO All contents below have to be refactored/cleaned-up!
        # fill the rowspan with a little table
        # parent is either an AR, a Worksheet, or a
        # ReferenceSample (analysis parent).
        parent = api.get_parent(obj)
        if parent.aq_parent.portal_type == "WorksheetFolder":
            # we're a duplicate; get original object's client
            client = obj.getAnalysis().aq_parent.aq_parent
        elif parent.aq_parent.portal_type == "Supplier":
            # we're a reference sample; get reference definition
            client = obj.getReferenceDefinition()
        else:
            client = parent.aq_parent
        pos_text = "<table class='worksheet-position' width='100%%' cellpadding='0' cellspacing='0' style='padding-bottom:5px;'><tr>" + \
                   "<td class='pos' rowspan='3'>%s</td>" % item['Pos']

        if obj.portal_type == 'ReferenceAnalysis':
            pos_text += "<td class='pos_top'>%s</td>" % obj.getReferenceAnalysesGroupID()
        elif obj.portal_type == 'DuplicateAnalysis' and \
                        obj.getAnalysis().portal_type == 'ReferenceAnalysis':
            pos_text += "<td class='pos_top'><a href='%s'>%s</a></td>" % \
                        (obj.aq_parent.absolute_url(), obj.aq_parent.id)
        elif client:
            pos_text += "<td class='pos_top'><a href='%s'>%s</a></td>" % \
                        (client.absolute_url(), client.Title())
        else:
            pos_text += "<td class='pos_top'>&nbsp;</td>"

        pos_text += "<td class='pos_top_icons' rowspan='3'>"
        if obj.portal_type == 'DuplicateAnalysis':
            pos_text += "<img title='%s' src='%s/++resource++bika.lims.images/duplicate.png'/>" % (
            _("Duplicate").encode('utf-8'), self.context.absolute_url())
            pos_text += "<br/>"
        elif obj.portal_type == 'ReferenceAnalysis' and obj.ReferenceType == 'b':
            pos_text += "<a href='%s'><img title='%s' src='++resource++bika.lims.images/blank.png'></a>" % (
            parent.absolute_url(), parent.Title())
            pos_text += "<br/>"
        elif obj.portal_type == 'ReferenceAnalysis' and obj.ReferenceType == 'c':
            pos_text += "<a href='%s'><img title='%s' src='++resource++bika.lims.images/control.png'></a>" % (
            parent.absolute_url(), parent.Title())
            pos_text += "<br/>"
        if parent.portal_type == 'AnalysisRequest':
            sample = parent.getSample()
            pos_text += "<a href='%s'><img title='%s' src='++resource++bika.lims.images/sample.png'></a>" % (
            sample.absolute_url(), sample.Title())
        pos_text += "</td></tr>"

        pos_text += "<tr><td>"
        if parent.portal_type == 'AnalysisRequest':
            pos_text += "<a href='%s'>%s</a>" % (
            parent.absolute_url(), parent.Title())
        elif parent.portal_type == 'ReferenceSample':
            pos_text += "<a href='%s'>%s</a>" % (
            parent.absolute_url(), parent.Title())
        elif obj.portal_type == 'DuplicateAnalysis':
            pos_text += "<a style='white-space:nowrap' href='%s'>%s</a>" % (
            obj.getAnalysis().aq_parent.absolute_url(),
            obj.getReferenceAnalysesGroupID())
        elif parent.portal_type == 'Worksheet':
            parent = obj.getAnalysis().aq_parent
            pos_text += "<a href='%s'>(%s)</a>" % (
            parent.absolute_url(), parent.Title())
        pos_text += "</td></tr>"

        # sampletype
        pos_text += "<tr><td>"
        if obj.portal_type == 'Analysis':
            pos_text += obj.aq_parent.getSample().getSampleType().Title()
        elif obj.portal_type == 'ReferenceAnalysis' or \
                (obj.portal_type == 'DuplicateAnalysis' and \
                             obj.getAnalysis().portal_type == 'ReferenceAnalysis'):
            pos_text += ""  # obj.aq_parent.getReferenceDefinition().Title()
        elif obj.portal_type == 'DuplicateAnalysis':
            pos_text += obj.getAnalysis().aq_parent.getSample().getSampleType().Title()
        pos_text += "</td></tr>"

        # samplingdeviation
        if obj.portal_type == 'Analysis':
            deviation = obj.aq_parent.getSample().getSamplingDeviation()
            if deviation:
                pos_text += "<tr><td>&nbsp;</td>"
                pos_text += "<td colspan='2'>"
                pos_text += deviation.Title()
                pos_text += "</td></tr>"

                ##            # barcode
                ##            barcode = parent.id.replace("-", "")
                ##            if obj.portal_type == 'DuplicateAnalysis':
                ##                barcode += "D"
                ##            pos_text += "<tr><td class='barcode' colspan='3'><div id='barcode_%s'></div>" % barcode + \
                ##                "<script type='text/javascript'>$('#barcode_%s').barcode('%s', 'code128', {'barHeight':15, addQuietZone:false, showHRI: false })</script>" % (barcode, barcode) + \
                ##                "</td></tr>"

        pos_text += "</table>"
        return pos_text
