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

from Acquisition import aq_base
from Acquisition import aq_parent
from senaite.core import logger
from zope.component import getAllUtilitiesRegisteredFor
from zope.intid.interfaces import IIntIds


def drop_intid_for_temporary_object(obj, event):
    """Unregister the intid that `five.intid` just created for a
    transient object held by a `TempFolder` (portal_factory).

    Plone's `PortalFactoryTool` materialises a content object
    inside a transient `TempFolder` whenever a user opens an add
    form so the form template can introspect the schema.  The
    transient parent is in-memory only, but `OFS.Folder._setObject`
    still fires `IObjectAddedEvent`, and `five.intid`'s subscriber
    eagerly registers a `KeyReferenceToPersistent` for the
    transient.  The keyref is committed at end-of-request (the
    intid utility's BTrees are persistent), while the transient
    itself is discarded — leaving an orphan keyref that pins the
    dead oid in storage forever.  On a busy install this leaks
    one orphan intid per add-form page load and accumulates into
    the hundreds of thousands.

    We run after `five.intid.addIntIdSubscriber` (registration
    order: that subscriber is loaded by the upstream package
    early in startup, ours later via this site's ZCML), inspect
    the freshly-added object, and undo the registration when the
    parent is a `TempFolder`.

    Restricting the check to `meta_type == "TempFolder"` keeps
    the subscriber narrow.  A real AR created via
    `_createObjectByType(client, tmpID())` is not held by a
    TempFolder, so its (UID-shaped) initial id and subsequent
    rename via `renameAfterCreation` are not affected — the
    standard add/move sequence still registers and then updates
    the keyref's path correctly.
    """
    parent = aq_parent(obj)
    if parent is None:
        return
    if getattr(aq_base(parent), "meta_type", "") != "TempFolder":
        return
    for intids in getAllUtilitiesRegisteredFor(IIntIds):
        try:
            intids.unregister(obj)
        except KeyError:
            # Object was never registered with this utility (some
            # types skip registration for their own reasons); the
            # matching upstream subscriber swallows the same error.
            continue
    logger.debug(
        "Dropped intid for TempFolder transient %r" % obj)
