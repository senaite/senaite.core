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

from bika.lims.interfaces import IInvalidated
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


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

    def get_retest(self):
        """Returns the retest of the current sample, if any
        """
        return self.sample.getRetest()
