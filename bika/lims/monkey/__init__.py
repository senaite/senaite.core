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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

import add_senaite_site  # noqa

from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.Archetypes import utils


def isFactoryContained(obj):
    """Are we inside the portal_factory?
    """
    if obj.isTemporary():
        return True
    parent = aq_parent(aq_inner(obj))
    if parent is None:
        # We don't have enough context to know where we are
        return False
    meta_type = getattr(aq_base(parent), "meta_type", "")
    return meta_type == "TempFolder"


# https://pypi.org/project/collective.monkeypatcher/#patching-module-level-functions
utils.isFactoryContained = isFactoryContained
