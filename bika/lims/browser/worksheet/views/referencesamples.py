# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import collections

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.worksheet.tools import showRejectionMessage
from bika.lims.permissions import EditWorksheet
from bika.lims.permissions import ManageWorksheets
from bika.lims.utils import get_link
from plone.memoize import view
from plone.protect import CheckAuthenticator


class ReferenceSamplesView(BikaListingView):
    """Displays reference control samples
    """

    def __init__(self, context, request):
        super(ReferenceSamplesView, self).__init__(context, request)

        self.catalog = "bika_catalog"
        self.contentFilter = {
            "portal_type": "ReferenceSample",
            "getSupportedServices": self.get_assigned_services_uids(),
            "isValid": True,
            "review_state": "current",
            "inactive_state": "active",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }

        self.context_actions = {}
        self.title = _("Add Control Reference")
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_column_toggles = False
        self.show_select_column = True
        self.show_categories = False
        self.pagesize = 999999
        self.allow_edit = True
        self.show_search = False

        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images/worksheet_big.png"
        )

        self.position_choices = []
        for pos in self.get_available_positions():
            self.position_choices.append({
                "ResultValue": pos,
                "ResultText": pos,
            })

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Reference Sample"),
                "sortable": False}),
            ("Position", {
                "title": _("Position"),
                "sortable": False}),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {},
                "transitions": [{"id": "add"}],
                "custom_transitions": [
                    {
                        "id": "add",
                        "title": _("Add"),
                        "url": self.__name__,
                    }
                ],
                "columns": self.columns.keys()
            },
        ]

    def __call__(self):
        template = super(ReferenceSamplesView, self).__call__()
        # TODO: Refactor Worfklow
        grant = self.is_edit_allowed() and self.is_manage_allowed()
        if not grant:
            redirect_url = api.get_url(self.context)
            return self.request.response.redirect(redirect_url)
        # TODO: Refactor this function call
        showRejectionMessage(self.context)
        # Handle form submission
        if self.request.form.get("submitted"):
            CheckAuthenticator(self.request)
            self.handle_submit()
        return template

    def update(self):
        """Update hook
        """
        super(ReferenceSamplesView, self).update()

    def handle_submit(self):
        """Handle form submission
        """
        form = self.request.form
        # Selected service UIDs
        uids = form.get("uids")
        # service -> reference mapping
        references = form.get("ReferenceSample")[0]
        # service -> position mapping
        positions = form.get("Position")[0]
        for uid in uids:
            reference_uid = references.get(uid)
            position = positions.get(uid)
            reference = api.get_object(reference_uid)
            self.context.addReferenceAnalyses(
                reference, [uid], dest_slot=position)
        redirect_url = "{}/{}".format(
            api.get_url(self.context), "manage_results")
        self.request.response.redirect(redirect_url)

    def show_categories_enabled(self):
        """Get the shwo category setting from the setup
        """
        return self.context.bika_setup.getCategoriseAnalysisServices()

    @view.memoize
    def is_edit_allowed(self):
        """Check if edit is allowed
        """
        checkPermission = self.context.portal_membership.checkPermission
        return checkPermission(EditWorksheet, self.context)

    @view.memoize
    def is_manage_allowed(self):
        """Check if manage is allowed
        """
        checkPermission = self.context.portal_membership.checkPermission
        return checkPermission(ManageWorksheets, self.context)

    @view.memoize
    def get_assigned_services(self):
        """Get the current assigned services of this Worksheet
        """
        analyses = self.context.getAnalyses()
        services = map(lambda an: an.getAnalysisService(), analyses)
        return services

    @view.memoize
    def get_assigned_services_uids(self):
        """Get the current assigned services UIDs of this Worksheet
        """
        services = self.get_assigned_services()
        uids = map(api.get_uid, services)
        return list(set(uids))

    @view.memoize
    def get_assigned_services_categories(self):
        """Get the current assigned services categories of this Worksheet
        """
        services = self.get_assigned_services()
        categories = map(lambda s: s.getCategoryTitle(), services)
        return sorted(list(set(categories)))

    @view.memoize
    def get_available_positions(self):
        """Return a list of empty slot numbers
        """
        available_positions = ["new"]
        layout = self.context.getLayout()
        used_positions = [int(slot["position"]) for slot in layout]
        if used_positions:
            used = [
                pos for pos in range(1, max(used_positions) + 1) if
                pos not in used_positions]
            available_positions.extend(used)
        return available_positions

    def get_available_reference_samples_for(self, service):
        """Returns the available reference samples for this service
        """
        query = {
            "portal_type": "ReferenceSample",
            "getSupportedServices": api.get_uid(service),
            "isValid": True,
            "review_state": "current",
            "inactive_state": "active",
            "sort_on": "sortable_title",
        }
        return map(api.get_object, api.search(query))

    def make_reference_sample_choices_for(self, service):
        """Create a choices list of available reference samples
        """
        reference_samples = self.get_available_reference_samples_for(service)
        choices = []
        for rs in reference_samples:
            text = api.get_title(rs)
            ref_def = rs.getReferenceDefinition()
            if ref_def:
                text += " ({})".format(api.get_title(ref_def))
            choices.append({
                "ResultText": text,
                "ResultValue": api.get_uid(rs),
            })
        return choices

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.

        The use of this service prevents the extra-loops in child objects.

        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """
        item = super(ReferenceSamplesView, self).folderitem(obj, item, index)

        # ensure we have an object and not a brain
        obj = api.get_object(obj)
        url = api.get_url(obj)
        title = api.get_title(obj)

        # Reference Sample
        item["Title"] = title
        item["replace"]["Title"] = get_link(url, value=title)

        # Reference Sample
        item["allow_edit"] = ["Position"]
        supported_services = obj.getSupportedServices()
        item["children"] = supported_services

        # Position
        item["Position"] = "new"
        item["choices"]["Position"] = self.position_choices

        return item

    def get_children_hook(self, parent_uid, child_uids=None):
        """Custom implenentation from ajax base class
        """
        children = []
        obj = api.get_object_by_uid(parent_uid)
        supported_services_uids = set(obj.getSupportedServices())
        supported_services = map(api.get_object, supported_services_uids)
        assigned_services = self.get_assigned_services()
        for service in supported_services:
            children.append({
                "id": api.get_id(service),
                "uid": api.get_uid(service),
                "title": api.get_title(service),
                "selected": service in assigned_services,
                "url": api.get_url(service),
                "parent": parent_uid,
                "allow_edit": [],
                "replace": {},
                "choices": {},
                "before": {},
                "after": {},
                "category": "None",
                "Title": api.get_title(service),
                "Position": "",

            })
        return children
