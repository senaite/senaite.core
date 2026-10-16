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


def on_method_added(method, event):
    """Set the instruments the method was created with

    The instruments reference a method by its UID, which a method only gets
    once it is created. Instruments passed in on creation are therefore kept
    by the setter and set here, once the method is in its container.

    :param method: the method that was added
    :param event: the IObjectAddedEvent
    """
    if not method.has_pending_instruments():
        return

    # An instrument links back to the method by looking its UID up in the
    # uid_catalog. The method is cataloged there by another subscriber of
    # this event, which may well run after this one, so catalog it first.
    # This is the very record that subscriber writes, it is updated in place
    uid_catalog = api.get_tool("uid_catalog")
    uid_catalog.catalog_object(method, api.get_uid_catalog_path(method))

    method.apply_pending_instruments()
