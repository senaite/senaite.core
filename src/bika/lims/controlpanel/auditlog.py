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

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.api.snapshot import compare_snapshots
from bika.lims.api.snapshot import get_last_snapshot
from bika.lims.api.snapshot import get_snapshot_by_version
from bika.lims.api.snapshot import get_snapshot_metadata
from bika.lims.api.snapshot import get_snapshot_version
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IAuditLog
from bika.lims.utils import get_link
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from zope.interface.declarations import implements


class AuditLogView(BikaListingView):

    def __init__(self, context, request):
        super(AuditLogView, self).__init__(context, request)

        self.catalog = "auditlog_catalog"

        self.contentFilter = {
            "sort_on": "snapshot_created",
            "sort_order": "desscending",
        }

        self.context_actions = {}

        self.title = self.context.translate(_("Audit Log"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images/auditlog_big.png"
        )

        self.show_select_column = False
        self.pagesize = 25

        self.columns = collections.OrderedDict((
            ("title", {
                "title": _("Title"),
                "index": "title"}),
            ("version", {
                "title": _("Version"),
                "index": "snapshot_version",
                "sortable": True}),
            ("modified", {
                "title": _("Date Modified"),
                "index": "modified",
                "sortable": True}),
            ("actor", {
                "title": _("Actor"),
                "index": "actor",
                "sortable": True}),
            ("fullname", {
                "title": _("Fullname"),
                "index": "fullname",
                "sortable": True}),
            ("roles", {
                "title": _("Roles"),
                "sortable": False,
                "toggle": False}),
            ("remote_address", {
                "title": _("Remote IP"),
                "sortable": True}),
            ("action", {
                "title": _("Action"),
                "index": "action",
                "sortable": True}),
            ("review_state", {
                "title": _("Workflow State"),
                "index": "review_state",
                "sortable": True}),
            ("diff", {
                "title": _("Changes"),
                "sortable": False}),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("Active"),
                "contentFilter": {},
                "columns": self.columns.keys(),
            }
        ]

    def before_render(self):
        """Before template render hook
        """
        # Don't allow any context actions
        self.request.set("disable_border", 1)

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.
        The use of this service prevents the extra-loops in child objects.
        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """
        obj = api.get_object(obj)

        # We are using the existing logic from the auditview
        logview = api.get_view("auditlog", context=obj, request=self.request)

        # get the last snapshot
        snapshot = get_last_snapshot(obj)
        # get the metadata of the last snapshot
        metadata = get_snapshot_metadata(snapshot)

        title = obj.Title()
        url = obj.absolute_url()
        auditlog_url = "{}/@@auditlog".format(url)

        # Title
        item["title"] = title
        # Link the title to the auditlog of the object
        item["replace"]["title"] = get_link(auditlog_url, value=title)

        # Version
        version = get_snapshot_version(obj, snapshot)
        item["version"] = version

        # Modification Date
        m_date = metadata.get("modified")
        item["modified"] = logview.to_localized_time(m_date)

        # Actor
        actor = metadata.get("actor")
        item["actor"] = actor

        # Fullname
        properties = api.get_user_properties(actor)
        item["fullname"] = properties.get("fullname", actor)

        # Roles
        roles = metadata.get("roles", [])
        item["roles"] = ", ".join(roles)

        # Remote Address
        remote_address = metadata.get("remote_address")
        item["remote_address"] = remote_address

        # Action
        action = metadata.get("action")
        item["action"] = logview.translate_state(action)

        # Review State
        review_state = metadata.get("review_state")
        item["review_state"] = logview.translate_state(review_state)

        # get the previous snapshot
        prev_snapshot = get_snapshot_by_version(obj, version-1)
        if prev_snapshot:
            prev_metadata = get_snapshot_metadata(prev_snapshot)
            prev_review_state = prev_metadata.get("review_state")
            if prev_review_state != review_state:
                item["replace"]["review_state"] = "{} &rarr; {}".format(
                    logview.translate_state(prev_review_state),
                    logview.translate_state(review_state))

            # Rendered Diff
            diff = compare_snapshots(snapshot, prev_snapshot)
            item["diff"] = logview.render_diff(diff)

        return item


schema = ATFolderSchema.copy()


class AuditLog(ATFolder):
    implements(IAuditLog)
    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(AuditLog, PROJECTNAME)
