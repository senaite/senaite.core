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
from senaite.core.catalog import SETUP_CATALOG
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@implementer(IVocabularyFactory)
class ReferenceDefinitionVocabulary(object):

    def __call__(self, context):
        reference_query = {
            "portal_type": "ReferenceDefinition",
            "is_active": True,
        }
        brains = api.search(reference_query, SETUP_CATALOG)
        definitions = map(api.get_object, brains)
        vocab = []
        for definition in definitions:
            uid = definition.UID()
            title = definition.Title()
            vocab.append(SimpleTerm(uid, uid, title))
        return SimpleVocabulary(vocab)


ReferenceDefinitionVocabularyFactory = ReferenceDefinitionVocabulary()
