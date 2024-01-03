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

from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from bika.lims import api


@implementer(IVocabularyFactory)
class ClientLandingPagesVocabulary(object):
    """Vocabulary factory for Client landing pages
    """

    skip = ["edit", "manage_access", "auditlog", ]

    def __call__(self, context):
        pt = api.get_tool("portal_types")
        type_info = pt.getTypeInfo("Client")
        terms = []
        for action in type_info.listActionInfos():
            if not action.get("visible", True):
                continue
            if action.get("id") in self.skip:
                continue
            url = action.get("url")
            if not url:
                continue

            # remove leading/trailing slashes
            url = url.strip("/")

            # create the vocab term
            title = action.get("title")
            term = SimpleTerm(url, url, title)
            terms.append(term)

        return SimpleVocabulary(terms)


ClientLandingPagesVocabularyFactory = ClientLandingPagesVocabulary()
