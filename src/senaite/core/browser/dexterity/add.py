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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims.api.snapshot import pause_snapshots_for
from bika.lims.api.snapshot import resume_snapshots_for
from plone.dexterity.browser.add import DefaultAddForm as BaseAddForm
from plone.dexterity.browser.add import DefaultAddView as BaseAddView


class DefaultAddForm(BaseAddForm):
    """Patched Add Form to handle renameAfterCreation of DX objects
    """

    def add(self, object):
        """Create a new object in a container
        """
        # Temporary disable snapshot creation for container
        pause_snapshots_for(self.container)
        super(DefaultAddForm, self).add(object)
        resume_snapshots_for(self.container)


class DefaultAddView(BaseAddView):
    form = DefaultAddForm
