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
from bika.lims import senaiteMessageFactory as _
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.schema.vocabulary import to_simple_vocabulary
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory


@implementer(IVocabularyFactory)
class AvailableMethods(object):
    """This function returns the registered methods in the system as a
    vocabulary.
    """

    def __call__(self, context):
        query = {
            "portal_type": "Method",
            "is_active": True,
        }
        brains = api.search(query, SETUP_CATALOG)
        items = [(b.UID, b.Title) for b in brains]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        items.insert(0, ("", _(u"title_method_not_specified",
                               default=u"Not specified")))
        return to_simple_vocabulary(items)


AvailableMethodsFactory = AvailableMethods()
