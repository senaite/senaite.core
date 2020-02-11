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

import collections
from operator import itemgetter

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.browser.analyses import AnalysesView as BaseView
from bika.lims.utils import get_image
from bika.lims.utils import t
from bika.lims.utils import to_int
from plone.memoize import view
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.interfaces import IRoutineAnalysis
from bika.lims.interfaces import IReferenceAnalysis
from bika.lims.interfaces import IDuplicateAnalysis


class AnalysesView(BaseView):
    """Manage Results View for Worksheet Analyses
    """

    def __init__(self, context, request):
        super(AnalysesView, self).__init__(context, request)

        self.context = context
        self.request = request

        self.analyst = None
        self.instrument = None

        self.contentFilter = {
            "getWorksheetUID": api.get_uid(context),
            "sort_on": "sortable_title",
        }

        self.icon = "{}/{}".format(
            self.portal_url,
            "++resource++bika.lims.images/worksheet_big.png"
        )

        self.allow_edit = True
        self.show_categories = False
        self.expand_all_categories = False
        self.show_search = False

        self.bika_setup = api.get_bika_setup()
        self.uids_strpositions = self.get_uids_strpositions()
        self.items_rowspans = dict()

        self.columns = collections.OrderedDict((
            ("Pos", {
                "sortable": False,
                "title": _("Position")}),
            ("Service", {
                "sortable": False,
                "title": _("Analysis")}),
            ("Method", {
                "sortable": False,
                "ajax": True,
                "title": _("Method")}),
            ("Instrument", {
                "sortable": False,
                "ajax": True,
                "title": _("Instrument")}),
            ("DetectionLimitOperand", {
                "title": _("DL"),
                "sortable": False,
                "ajax": True,
                "autosave": True,
                "toggle": False}),
            ("Result", {
                "title": _("Result"),
                "ajax": True,
                "sortable": False}),
            ("retested", {
                "title": get_image("retested.png", title=t(_("Retested"))),
                "toggle": False,
                "type": "boolean"}),
            ("Specification", {
                "title": _("Specification"),
                "sortable": False}),
            ("Uncertainty", {
                "sortable": False,
                "title": _("+-")}),
            ("DueDate", {
                "sortable": False,
                "title": _("Due Date")}),
            ("state_title", {
                "sortable": False,
                "title": _("State")}),
            ("Attachments", {
                "sortable": False,
                "title": _("Attachments")}),
        ))

        # Inject Remarks column for listing
        if self.is_analysis_remarks_enabled():
            self.columns["Remarks"] = {
                "title": "Remarks",
                "ajax": True,
                "toggle": False,
                "sortable": False,
                "type": "remarks"
            }

        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns.keys(),
            },
        ]

    @view.memoize
    def is_analysis_remarks_enabled(self):
        """Check if analysis remarks are enabled
        """
        return self.context.bika_setup.getEnableAnalysisRemarks()

    def isItemAllowed(self, obj):
        """Returns true if the current analysis to be rendered has a slot
        assigned for the current layout.

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
        """Applies new properties to the item (analysis) that is currently
        being rendered as a row in the list.

        :param obj: analysis to be rendered as a row in the list
        :param item: dict representation of the analysis, suitable for the list
        :param index: current position of the item within the list
        :type obj: ATContentType/DexterityContentType
        :type item: dict
        :type index: int
        :return: the dict representation of the item
        :rtype: dict
        """
        item = super(AnalysesView, self).folderitem(obj, item, index)
        item_obj = api.get_object(obj)
        uid = item["uid"]

        # Slot is the row position where all analyses sharing the same parent
        # (eg. AnalysisRequest, SampleReference), will be displayed as a group
        slot = self.get_item_slot(uid)
        item["Pos"] = slot

        # The position string contains both the slot + the position of the
        # analysis within the slot: "position_sortkey" will be used to sort all
        # the analyses to be displayed in the list
        str_position = self.uids_strpositions[uid]
        item["pos_sortkey"] = str_position

        item["colspan"] = {"Pos": 1}
        item["Service"] = item_obj.Title()
        item["Category"] = item_obj.getCategoryTitle()
        item["DueDate"] = self.ulocalized_time(item_obj, long_format=0)
        item["class"]["Service"] = "service_title"

        # To prevent extra loops, we compute here the number of analyses to be
        # rendered within each slot. This information will be useful later for
        # applying rowspan to the first cell of each slot, that contains info
        # about the parent of all the analyses contained in that slot (e.g
        # Analysis Request ID, Sample Type, etc.)
        rowspans = self.items_rowspans.get(slot, 0) + 1

        remarks_enabled = self.is_analysis_remarks_enabled()
        if remarks_enabled:
            # Increase in one unit the rowspan, cause the comment field for
            # this analysis will be rendered in a new row, below the row that
            # displays the current item
            rowspans = rowspans + 1
        # We map this rowspan information in items_rowspan, that will be used
        # later during the rendereing of slot headers (first cell of each row)
        self.items_rowspans[slot] = rowspans

        return item

    def folderitems(self):
        """Returns an array of dictionaries, each dictionary represents an
        analysis row to be rendered in the list. The array returned is sorted
        in accordance with the layout positions set for the analyses this
        worksheet contains when the analyses were added in the worksheet.

        :returns: list of dicts with the items to be rendered in the list
        """
        items = BaseView.folderitems(self)

        # Fill empty positions from the layout with fake rows. The worksheet
        # can be generated by making use of a WorksheetTemplate, so there is
        # the chance that some slots of this worksheet being empty. We need to
        # render a row still, at lest to display the slot number (Pos)
        self.fill_empty_slots(items)

        # Sort the items in accordance with the layout
        items = sorted(items, key=itemgetter("pos_sortkey"))

        # Fill the slot header cells (first cell of each row). Each slot
        # contains the analyses that belong to the same parent
        # (AnalysisRequest, ReferenceSample), so the information about the
        # parent must be displayed in the first cell of each slot.
        self.fill_slots_headers(items)

        return items

    def get_uids_strpositions(self):
        """Returns a dict with the positions of each analysis within the
        current worksheet in accordance with the current layout. The key of the
        dict is the uid of the analysis and the value is an string
        representation of the full position of the analysis within the list:

            {<analysis_uid>: '<slot_number>:<position_within_slot>',}

        :returns: a dictionary with the full position within the worksheet of
                  all analyses defined in the current layout.
        """
        uids_positions = dict()
        layout = self.context.getLayout()
        layout = layout and layout or []
        # Map the analysis uids with their positions.
        occupied = []
        next_positions = {}
        for item in layout:
            uid = item.get("analysis_uid", "")
            slot = int(item["position"])
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
        """Returns a list with the position for the analysis_uid passed in
        within the current worksheet in accordance with the current layout,
        where the first item from the list returned is the slot and the second
        is the position of the analysis within the slot.

        :param analysis_uid: uid of the analysis the position is requested
        :return: the position (slot + position within slot) of the analysis
        :rtype: list
        """
        str_position = self.uids_strpositions.get(analysis_uid, "")
        tokens = str_position.split(":")
        if len(tokens) != 2:
            return None
        return [to_int(tokens[0]), to_int(tokens[1])]

    def get_item_slot(self, analysis_uid):
        """Returns the slot number where the analysis must be rendered. An slot
        contains all analyses that belong to the same parent (AnalysisRequest,
        ReferenceSample).

        :param analysis_uid: the uid of the analysis the slot is requested
        :return: the slot number where the analysis must be rendered
        """
        position = self.get_item_position(analysis_uid)
        if not position:
            return None
        return position[0]

    def _get_slots(self, empty_uid=False):
        """Returns a list with the position number of the slots that are
        occupied (if empty_uid=False) or are empty (if empty_uid=True)

        :param empty_uid: True exclude occupied slots. False excludes empties
        :return: sorted list with slot numbers
        """
        slots = list()
        for uid, position in self.uids_strpositions.items():
            if empty_uid and not uid.startswith("empty-"):
                continue
            elif not empty_uid and uid.startswith("empty-"):
                continue
            tokens = position.split(":")
            slots.append(to_int(tokens[0]))
        return sorted(list(set(slots)))

    def get_occupied_slots(self):
        """Returns the list of occupied slots, those that have at least one
        analysis assigned according to the current layout. Delegates to
        self._get_slots(empty_uid=False)

        :return: list of slot numbers that at least have one analysis assigned
        """
        return self._get_slots(empty_uid=False)

    def get_empty_slots(self):
        """Returns the list of empty slots, those that don't have any analysis
        assigned according to the current layout.

        Delegates to self._get_slots(empty_uid=True)

        :return: list of slot numbers that don't have any analysis assigned
        """
        return self._get_slots(empty_uid=True)

    def fill_empty_slots(self, items):
        """Append dicts to the items passed in for those slots that don't have
        any analysis assigned but the row needs to be rendered still.

        :param items: dictionary with the items to be rendered in the list
        """
        for pos in self.get_empty_slots():
            item = {
                "obj": self.context,
                "id": self.context.id,
                "uid": self.context.UID(),
                "title": self.context.Title(),
                "type_class": "blank-worksheet-row",
                "url": self.context.absolute_url(),
                "relative_url": self.context.absolute_url(),
                "view_url": self.context.absolute_url(),
                "path": "/".join(self.context.getPhysicalPath()),
                "before": {},
                "after": {},
                "replace": {
                    "Pos": "<span class='badge'>{}</span> {}".format(
                        pos, _("Reassignable Slot"))
                },
                "choices": {},
                "class": {},
                "state_class": "state-empty",
                "allow_edit": [],
                "Pos": pos,
                "pos_sortkey": "{:010}:{:010}".format(pos, 1),
                "Service": "",
                "Attachments": "",
                "state_title": "",
                "disabled": True,
            }

            items.append(item)

    def fill_slots_headers(self, items):
        """Generates the header cell for each slot. For each slot, the first
        cell displays information about the parent all analyses within that
        given slot have in common, such as the AR Id, SampleType, etc.

        :param items: dictionary with items to be rendered in the list
        """
        prev_position = 0
        for item in items:
            item_position = item["Pos"]
            if item_position == prev_position:
                item = self.skip_item_key(item, "Pos")
                # head slot already filled
                continue
            if item.get("disabled", False):
                # empty slot
                continue

            # This is the first analysis found for the given position, add the
            # slot info in there and apply a rowspan accordingly.
            rowspan = self.items_rowspans.get(item_position, 1)
            prev_position = item_position
            item["rowspan"] = {"Pos": rowspan}
            item["replace"]["Pos"] = self.get_slot_header(item)

    def skip_item_key(self, item, key):
        """Add the key to the item's "skip" list
        """
        if "skip" in item:
            item["skip"].append(key)
        else:
            item["skip"] = [key]
        return item

    def get_slot_header(self, item):
        """Generates a slot header (the first cell of the row) for the item

        :param item: the item for which the slot header is requested
        :return: the html contents to be displayed in the first cell of a slot
        """
        obj = item["obj"]
        obj = api.get_object(obj)

        # Prepare the template data
        data = {
            "obj": obj,
            "item": item,
            "position": item["Pos"],
        }
        # update the data
        data.update(self.get_slot_header_data(obj))

        template = ViewPageTemplateFile("../templates/slot_header.pt")
        return template(self, data=data)

    def get_slot_header_data(self, obj):
        """Prepare the data for the slot header template
        """

        item_obj = None
        item_title = ""
        item_url = ""
        item_img = ""
        item_img_url = ""
        item_img_text = ""
        additional_item_icons = []

        parent_obj = None
        parent_title = ""
        parent_url = ""
        parent_img = ""
        parent_img_text = ""
        additional_parent_icons = []

        sample_type_obj = None
        sample_type_title = ""
        sample_type_url = ""
        sample_type_img = ""
        sample_type_img_text = ""

        if IDuplicateAnalysis.providedBy(obj):
            # item
            request = obj.getRequest()
            item_obj = request
            item_title = api.get_id(request)
            item_url = api.get_url(request)
            item_img = "duplicate.png"
            item_img_url = api.get_url(request)
            item_img_text = t(_("Duplicate"))
            # additional item icons
            additional_item_icons.append(
                self.render_remarks_tag(request))
            # parent
            client = request.getClient()
            parent_obj = client
            parent_title = api.get_title(client)
            parent_url = api.get_url(client)
            parent_img = "client.png"
            parent_img_text = t(_("Client"))
            # sample type
            sample_type = request.getSampleType()
            sample_type_title = request.getSampleTypeTitle()
            sample_type_url = api.get_url(sample_type)
            sample_type_img = "sampletype.png"
            sample_type_img_text = t(_("Sample Type"))
        elif IReferenceAnalysis.providedBy(obj):
            # item
            sample = obj.getSample()
            item_obj = sample
            item_title = api.get_id(sample)
            item_url = api.get_url(sample)
            item_img_url = api.get_url(sample)
            item_img = "control.png"
            item_img_text = t(_("Control"))
            if obj.getReferenceType() == "b":
                item_img = "blank.png"
                item_img_text = t(_("Blank"))
            # parent
            supplier = obj.getSupplier()
            parent_obj = supplier
            parent_title = api.get_title(supplier)
            parent_url = api.get_url(supplier)
            parent_img = "supplier.png"
            parent_img_text = t(_("Supplier"))
        elif IRoutineAnalysis.providedBy(obj):
            # item
            request = obj.getRequest()
            item_obj = request
            item_title = api.get_id(request)
            item_url = api.get_url(request)
            item_img = "sample.png"
            item_img_url = api.get_url(request)
            item_img_text = t(_("Sample"))
            # additional item icons
            additional_item_icons.append(
                self.render_remarks_tag(request))
            # parent
            client = obj.getClient()
            parent_obj = client
            parent_title = api.get_title(client)
            parent_url = api.get_url(client)
            parent_img = "client.png"
            parent_img_text = t(_("Client"))
            # sample type
            sample_type = obj.getSampleType()
            sample_type_title = obj.getSampleTypeTitle()
            sample_type_url = api.get_url(sample_type)
            sample_type_img = "sampletype.png"
            sample_type_img_text = t(_("Sample Type"))

        return {
            # item
            "item_obj": item_obj,
            "item_title": item_title,
            "item_url": item_url,
            "item_img": get_image(item_img, title=item_img_text),
            "item_img_url": item_img_url,
            "additional_item_icons": additional_item_icons,
            # parent
            "parent_obj": parent_obj,
            "parent_title": parent_title,
            "parent_url": parent_url,
            "parent_img": get_image(parent_img, title=parent_img_text),
            "additional_parent_icons": additional_parent_icons,
            # sample type
            "sample_type_obj": sample_type_obj,
            "sample_type_title": sample_type_title,
            "sample_type_url": sample_type_url,
            "sample_type_img": get_image(
                sample_type_img, title=sample_type_img_text),
        }

    def render_remarks_tag(self, ar):
        """Renders a remarks image icon
        """
        if not ar.getRemarks():
            return ""

        uid = api.get_uid(ar)
        url = ar.absolute_url()
        title = ar.Title()
        tooltip = _("Remarks of {}").format(title)

        # Note: The 'href' is picked up by the overlay handler, see
        #       bika.lims.worksheet.coffee
        attrs = {
            "css_class": "slot-remarks",
            "style": "cursor: pointer;",
            "title": tooltip,
            "uid": uid,
            "href": "{}/base_view".format(url),
        }

        return get_image("remarks_ico.png", **attrs)
