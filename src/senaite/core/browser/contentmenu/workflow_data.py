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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims.decorators import returns_json
from plone.protect.utils import addTokenToUrl
from Products.Five import BrowserView
from senaite.core.decorators import readonly_transaction
from senaite.core.i18n import translate


HIDE_WF_ITEMS = ("workflow-transition-advanced",)

# Mirrors plone.app.contentmenu.menu.WorkflowMenu.getMenuItems: only
# transitions with `category="workflow"` belong in the WF menu.
# Transitions declared with other categories (e.g. "listing") are
# intentionally hidden from the menu and can only be invoked from
# their respective contexts (such as the samples listing's batch
# transition buttons).
WORKFLOW_ACTION_CATEGORY = "workflow"


class WorkflowMenuDataView(BrowserView):
    """JSON payload for the lazy workflow menu.

    Returns the current review state plus the list of allowed
    transitions for the current user on `self.context`.
    """

    @returns_json
    @readonly_transaction
    def __call__(self):
        self.request.response.setHeader("Cache-Control", "no-store")
        wf_tool = api.get_tool("portal_workflow")
        return {
            "uid": api.get_uid(self.context),
            "state": self.get_state(wf_tool),
            "transitions": self.get_transitions(wf_tool),
        }

    def translate(self, msg):
        """Translate `msg` against the current request locale, using
        the `senaite.core` domain by default (overridden when the
        msgid is a `Message` with its own domain).
        """
        if not msg:
            return msg
        return translate(msg)

    def get_state(self, wf_tool):
        """Return the current review state info
        """
        review_state = wf_tool.getInfoFor(
            self.context, "review_state", "")
        title = self.get_state_title(wf_tool, review_state)
        return {
            "id": review_state,
            "title": self.translate(title),
            "css_class": "state-{}".format(review_state),
        }

    def get_state_title(self, wf_tool, review_state):
        """Look up the raw (untranslated) title of the given review
        state.
        """
        workflows = wf_tool.getWorkflowsFor(self.context) or []
        for wf in workflows:
            state = wf.states.get(review_state)
            if state is not None:
                return state.title or review_state
        return review_state

    def get_transitions(self, wf_tool):
        """Return the allowed transitions as a list of dicts,
        sorted alphabetically by the translated title.

        Only transitions in the `workflow` action category are
        returned. Listing-only transitions (e.g. `multi_results`,
        `duplicate_sample`) are intentionally excluded so the menu
        matches the behavior of the stock Plone workflow menu.

        Uses `listActionInfos` (rather than `getTransitionsFor`)
        because the latter does not expose the `category` field
        we need for filtering.
        """
        actions = wf_tool.listActionInfos(object=self.context) or []
        infos = [self.transition_info(a) for a in actions
                 if a.get("category") == WORKFLOW_ACTION_CATEGORY
                 and a.get("id") not in HIDE_WF_ITEMS
                 and a.get("allowed")]
        infos.sort(key=lambda i: (i["title"] or "").lower())
        return infos

    def transition_info(self, transition):
        """Reduce a transition dict to what the UI needs and translate
        the user-visible strings.
        """
        tid = transition.get("id", "")
        title = (transition.get("title")
                 or transition.get("name")
                 or tid)
        return {
            "id": tid,
            "title": self.translate(title),
            "url": self.transition_url(transition),
            "description": self.translate(
                transition.get("description", "")),
        }

    def transition_url(self, transition):
        """Return the URL to trigger the transition.

        Mirrors plone.app.contentmenu.menu.WorkflowMenu.getMenuItems:
        when the transition's `actbox_url` is empty (the default for
        most SENAITE workflows) we fall back to the standard
        `content_status_modify` handler, and we always append the
        CSRF authenticator token expected by `plone.protect`.
        """
        action_url = transition.get("url") or ""
        if not action_url:
            action_url = "{0}/content_status_modify?workflow_action={1}"
            action_url = action_url.format(
                self.context.absolute_url(),
                transition.get("id", ""),
            )
        return addTokenToUrl(action_url, self.request)
