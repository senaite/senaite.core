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
# Copyright 2018-2023 by it's authors.
# Some rights reserved, see README and LICENSE.

from senaite.core.config.operators import GREATER_THAN_OPERATORS
from senaite.core.config.operators import LOWER_THAN_OPERATORS
from senaite.core.vocabularies import to_simple_vocabulary
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory


@implementer(IVocabularyFactory)
class LowerThanOperators(object):

    def __call__(self, context):
        return to_simple_vocabulary(LOWER_THAN_OPERATORS)


@implementer(IVocabularyFactory)
class GreaterThanOperators(object):

    def __call__(self, context):
        return to_simple_vocabulary(GREATER_THAN_OPERATORS)


LowerThanOperatorsFactory = LowerThanOperators()
GreaterThanOperatorsFactory = GreaterThanOperators()
