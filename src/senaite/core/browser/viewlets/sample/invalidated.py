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
from bika.lims.interfaces import IInvalidated
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.api.dtime import to_localized_time


class InvalidatedSampleViewlet(ViewletBase):
    """Print a viewlet to display a message stating the Sample was invalidated,
    along with a link to the retest and the invalidation reason
    """
    index = ViewPageTemplateFile("templates/invalidated.pt")

    @property
    def sample(self):
        """Returns the sample of current context
        """
        return self.context

    def is_visible(self):
        """Returns whether this viewlet must be visible or not
        """
        return self.is_invalidated()

    def is_invalidated(self):
        """Returns whether the current sample was invalidated
        """
        return IInvalidated.providedBy(self.sample)

    def get_invalidation_info(self):
        """Returns the information about the last invalidation transition that
        took place for the current sample
        """
        # get the review history (newest first)
        history = api.get_review_history(self.sample)
        for event in history:
            if event.get("action") != "invalidate":
                continue
            dt = event.get("time")
            actor = event.get("actor")
            comments = event.get("comments", "")
            return {
                "actor": actor,
                "fullname": self.get_fullname(actor),
                "date": to_localized_time(dt, long_format=True),
                "comment": api.safe_unicode(comments),
            }

        return {}

    def get_fullname(self, actor):
        """Returns the fullname of the user passed-in
        """
        user = api.get_user(actor)
        if not user:
            return actor

        props = api.get_user_properties(user)
        fullname = props.get("fullname", actor)
        contact = api.get_user_contact(user)
        fullname = contact and contact.getFullname() or fullname
        return fullname


    def get_retest(self):
        """Returns the retest of the current sample, if any
        """
        return self.sample.getRetest()
