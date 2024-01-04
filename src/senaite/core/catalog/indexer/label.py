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

from bika.lims import api
from plone.indexer import indexer
from senaite.core.api import label as label_api
from senaite.core.interfaces import IHaveLabels


@indexer(IHaveLabels)
def labels(instance):
    """Returns a list of labels for the given instance
    """
    labels = label_api.get_obj_labels(instance)
    return map(api.safe_unicode, labels)


@indexer(IHaveLabels)
def listing_searchable_text(instance):
    """Retrieves most commonly searched values for fulltext search

    :returns: string with search terms
    """
    entries = set()

    labels = label_api.get_obj_labels(instance)
    if labels:
        entries.update(set(labels))

    entries.add(instance.getId())
    entries.add(instance.Title())

    return u" ".join(map(api.safe_unicode, entries))
