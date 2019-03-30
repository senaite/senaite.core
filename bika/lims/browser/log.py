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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

import collections

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from plone.memoize import view
from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.content import ContentHistoryView


class LogView(BikaListingView):
    """Review/Revision log view
    """

    template = ViewPageTemplateFile("templates/log.pt")

    def __init__(self, context, request):
        super(LogView, self).__init__(context, request)

        self.show_select_column = False
        self.pagesize = 999999
        self.show_search = False

        self.icon = "{}/{}/{}".format(
            self.portal_url,
            "++resource++bika.lims.images",
            "%s_big.png" % context.portal_type.lower(),
        )

        self.title = "{} Log".format(api.get_title(context))

        self.columns = collections.OrderedDict((
            ("Version", {
                "title": _("Version"), "sortable": False}),
            ("Date", {
                "title": _("Date"), "sortable": False}),
            ("Actor", {
                "title": _("Actor"), "sortable": False}),
            ("Action", {
                "title": _("Action"), "sortable": False}),
            ("State", {
                "title": _("Outcome state"), "sortable": False}),
        ))

        # Do not display Version column if the content is not versionable
        if not self.is_versionable():
            del(self.columns["Version"])

        self.review_states = [
            {
                "id": "default",
                "title": "All",
                "contentFilter": {},
                "columns": self.columns.keys(),
            }
        ]

    def is_versionable(self):
        """Checks if the content is versionable
        """
        pr = api.get_tool("portal_repository")
        return pr.isVersionable(self.context)

    def update(self):
        """Update hook
        """
        super(LogView, self).update()
        self.total = len(self.get_full_history())

    def is_versioning_entry(self, entry):
        """Checks if the entry is a versioning entry
        """
        return entry.get("type") == "versioning"

    def to_title(self, id):
        """Convert an id to a human readable title
        """
        if not isinstance(id, basestring):
            return id
        return id.capitalize().replace("_", " ")

    def get_revision_history(self):
        """Return the revision history of the current context
        """
        chv = ContentHistoryView(self.context, self.request)
        return chv.revisionHistory()

    def get_review_history(self):
        """Return the review history of the current context
        """
        return api.get_review_history(self.context)

    @view.memoize
    def get_full_history(self):
        history = self.get_revision_history() + self.get_review_history()
        if len(history) == 0:
            return []
        history.sort(key=lambda x: x["time"], reverse=True)
        return history

    def get_entry_version(self, entry, default=0):
        """Return the version of the entry
        """
        version = entry.get("version_id", default) or default
        return version

    def get_entry_date(self, entry):
        """Return the action date
        """
        date = DateTime(entry.get("time"))
        return self.ulocalized_time(date, long_format=1),

    def get_entry_actor(self, entry):
        """Return the fullname of the actor
        """
        actor = None
        if self.is_versioning_entry(entry):
            # revision entries have an actor dict
            actor_dict = entry.get("actor")
            actor = actor_dict.get("fullname") or actor_dict.get("actorid")
        else:
            # review history items have only an actor id
            actor = entry.get("actor")
            # try to get the fullname
            props = api.get_user_properties(actor)
            actor = props.get("fullname") or actor
        # automatic transitions have no actor
        if actor is None:
            return ""
        return actor

    def get_entry_action(self, entry):
        """Return the action
        """
        action = None
        if self.is_versioning_entry(entry):
            # revision entries have a transition_title
            action = entry.get("transition_title")
        else:
            # review history items have only an action
            action = entry.get("action")
        # automatic transitions have no action
        if action is None:
            return ""
        # make the action human readable
        return _(self.to_title(action))

    def get_entry_state(self, entry):
        """Return the state
        """
        state = None
        if self.is_versioning_entry(entry):
            # revision entries have no state
            new_version = self.get_entry_version(entry)
            state = "{}: {}".format(_("Version"), new_version)
        else:
            # review history items have a state id
            state = entry.get("review_state")
        if not state:
            return ""
        return _(self.to_title(state))

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

    def make_log_entry(self, entry, index):
        """Create a log entry
        """
        item = self.make_empty_item(**entry)

        item["Version"] = self.get_entry_version(entry)
        item["Date"] = self.get_entry_date(entry)
        item["Actor"] = self.get_entry_actor(entry)
        item["Action"] = self.get_entry_action(entry)
        item["State"] = self.get_entry_state(entry)

        return item

    def folderitems(self):
        """Generate folderitems for each review history item
        """
        items = []

        history = self.get_full_history()
        for num, entry in enumerate(history):
            items.append(self.make_log_entry(entry, num))
        return items
