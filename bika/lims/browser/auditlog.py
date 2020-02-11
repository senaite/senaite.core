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
from bika.lims.api.snapshot import get_snapshot_by_version
from bika.lims.api.snapshot import get_snapshot_metadata
from bika.lims.api.snapshot import get_snapshot_version
from bika.lims.api.snapshot import get_snapshots
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.interfaces import IAuditable
from bika.lims.utils import t
from plone.memoize import view
from Products.CMFPlone.i18nl10n import ulocalized_time
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class HasAuditLog(BrowserView):
    """Helper View to check if the context provides the IAuditable interface
    """
    def __call__(self):
        return IAuditable.providedBy(self.context)


class AuditLogView(BikaListingView):
    """Audit View
    """
    template = ViewPageTemplateFile("templates/auditlog.pt")
    diff_template = ViewPageTemplateFile("templates/auditlog_diff.pt")

    def __init__(self, context, request):
        super(AuditLogView, self).__init__(context, request)

        # Query is ignored in `folderitems` method and only there to override
        # the default settings
        self.catalog = "uid_catalog"
        self.contentFilter = {"UID": api.get_uid(context)}

        # TODO: Fix in senaite.core.listing.get_api_url
        #
        # Set the view name with `@@` prefix to get the right API URL on the
        # the setup folder
        self.__name__ = "@@auditlog"

        self.show_select_column = False
        self.show_search = False
        self.pagesize = 5

        self.icon = "{}/{}/{}".format(
            self.portal_url,
            "++resource++bika.lims.images",
            "%s_big.png" % context.portal_type.lower())

        self.title = "Audit Log for {}".format(api.get_title(context))

        self.columns = collections.OrderedDict((
            ("version", {
                "title": _("Version"), "sortable": False}),
            ("modified", {
                "title": _("Date Modified"), "sortable": False}),
            ("actor", {
                "title": _("Actor"), "sortable": False}),
            ("fullname", {
                "title": _("Fullname"), "sortable": False}),
            ("roles", {
                "title": _("Roles"), "sortable": False, "toggle": False}),
            ("remote_address", {
                "title": _("Remote IP"), "sortable": False}),
            ("action", {
                "title": _("Action"), "sortable": False}),
            ("review_state", {
                "title": _("Workflow State"), "sortable": False}),
            ("diff", {
                "title": _("Changes"), "sortable": False}),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": "All",
                "contentFilter": {},
                "columns": self.columns.keys(),
            }
        ]

    def update(self):
        """Update hook
        """
        super(AuditLogView, self).update()

    def make_empty_item(self, **kw):
        """Create a new empty item
        """
        item = {
            "uid": None,
            "before": {},
            "after": {},
            "replace": {},
            "allow_edit": [],
            "disabled": False,
            "state_class": "state-active",
        }
        item.update(**kw)
        return item

    @view.memoize
    def get_widget_for(self, fieldname):
        """Lookup the widget
        """
        field = self.context.getField(fieldname)
        if not field:
            return None
        return field.widget

    def get_widget_label_for(self, fieldname, default=None):
        """Lookup the widget of the field and return the label
        """
        widget = self.get_widget_for(fieldname)
        if widget is None:
            return default
        return widget.label

    def to_localized_time(self, date, **kw):
        """Converts the given date to a localized time string
        """
        date = api.to_date(date, default=None)
        if date is None:
            return ""
        # default options
        options = {
            "long_format": True,
            "time_only": False,
            "context": self.context,
            "request": self.request,
            "domain": "senaite.core",
        }
        options.update(kw)
        return ulocalized_time(date, **options)

    def render_diff(self, diff):
        """Render the diff template

        :param diff: Dictionary of fieldname -> diffs
        :returns: Rendered HTML template
        """
        return self.diff_template(self, diff=diff)

    def translate_state(self, s):
        """Translate the given state string
        """
        if not isinstance(s, basestring):
            return s
        s = s.capitalize().replace("_", " ")
        return t(_(s))

    def folderitems(self):
        """Generate folderitems for each version
        """
        items = []
        # get the snapshots
        snapshots = get_snapshots(self.context)
        # reverse the order to get the most recent change first
        snapshots = list(reversed(snapshots))
        # set the total number of items
        self.total = len(snapshots)
        # slice a batch
        batch = snapshots[self.limit_from:self.limit_from+self.pagesize]

        for snapshot in batch:
            item = self.make_empty_item(**snapshot)
            # get the version of the snapshot
            version = get_snapshot_version(self.context, snapshot)

            # Version
            item["version"] = version

            # get the metadata of the diff
            metadata = get_snapshot_metadata(snapshot)

            # Modification Date
            m_date = metadata.get("modified")
            item["modified"] = self.to_localized_time(m_date)

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
            item["action"] = self.translate_state(action)

            # Review State
            review_state = metadata.get("review_state")
            item["review_state"] = self.translate_state(review_state)

            # get the previous snapshot
            prev_snapshot = get_snapshot_by_version(self.context, version-1)
            if prev_snapshot:
                prev_metadata = get_snapshot_metadata(prev_snapshot)
                prev_review_state = prev_metadata.get("review_state")
                if prev_review_state != review_state:
                    item["replace"]["review_state"] = "{} &rarr; {}".format(
                        self.translate_state(prev_review_state),
                        self.translate_state(review_state))

                # Rendered Diff
                diff = compare_snapshots(snapshot, prev_snapshot)
                item["diff"] = self.render_diff(diff)

            # append the item
            items.append(item)

        return items
