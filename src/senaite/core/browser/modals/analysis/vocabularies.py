# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the Free
# Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA.
#
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.config import LDL
from bika.lims.config import UDL
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


def get_analysis(context):
    """Extract the real AT analysis from proxy or direct object
    """
    return getattr(context, "_analysis", context)


@implementer(IVocabularyFactory)
class AnalysisMethodsVocabulary(object):
    """Vocabulary of allowed methods for an analysis
    """

    def __call__(self, context):
        analysis = get_analysis(context)
        methods = analysis.getAllowedMethods()
        default_method = analysis.getMethod()
        items = []
        for method in methods:
            uid = api.get_uid(method)
            title = api.get_title(method)
            items.append(SimpleTerm(uid, uid, title))
        if not methods:
            items = [SimpleTerm("", "", _(u"None"))]
        elif default_method is None:
            items.insert(0, SimpleTerm("", "", _(u"None")))
        return SimpleVocabulary(items)


@implementer(IVocabularyFactory)
class AnalysisInstrumentsVocabulary(object):
    """Vocabulary of allowed instruments for an analysis,
    filtered by current method
    """

    def __call__(self, context):
        analysis = get_analysis(context)
        instruments = analysis.getAllowedInstruments()
        method = analysis.getMethod()
        if method:
            method_instruments = method.getInstruments()
            instruments = list(
                set(instruments).intersection(
                    method_instruments
                )
            )
        items = [SimpleTerm("", "", _(u"None"))]
        for instrument in instruments:
            if instrument.isValid():
                uid = api.get_uid(instrument)
                title = api.get_title(instrument)
                items.append(SimpleTerm(uid, uid, title))
        items.sort(key=lambda x: x.title or "")
        return SimpleVocabulary(items)


@implementer(IVocabularyFactory)
class AnalysisAnalystsVocabulary(object):
    """Vocabulary of available analysts
    """

    def __call__(self, context):
        users = api.get_users_by_roles(
            ["Manager", "LabManager", "Analyst"]
        )
        items = []
        for user in users:
            username = user.getUserName()
            fullname = api.get_user_fullname(username)
            display = fullname or username
            items.append(
                SimpleTerm(username, username, display)
            )
        items.sort(key=lambda x: (x.title or "").lower())
        return SimpleVocabulary(items)


@implementer(IVocabularyFactory)
class AnalysisUnitsVocabulary(object):
    """Vocabulary of unit choices for an analysis
    """

    def __call__(self, context):
        analysis = get_analysis(context)
        choices = analysis.getUnitChoices() or []
        items = []
        for choice in choices:
            value = choice.get("value", "")
            items.append(SimpleTerm(value, value, value))
        return SimpleVocabulary(items)


@implementer(IVocabularyFactory)
class AnalysisDLOperandsVocabulary(object):
    """Vocabulary of detection limit operands
    """

    def __call__(self, context):
        items = [
            SimpleTerm("", "", ""),
            SimpleTerm(LDL, LDL, LDL),
            SimpleTerm(UDL, UDL, UDL),
        ]
        return SimpleVocabulary(items)


@implementer(IVocabularyFactory)
class AnalysisResultOptionsVocabulary(object):
    """Vocabulary of result options for select-type results
    """

    def __call__(self, context):
        analysis = get_analysis(context)
        options = analysis.getResultOptions() or []
        sort_by = analysis.getResultOptionsSorting()
        if sort_by:
            sort_key, sort_order = sort_by.split("-")
            reverse = sort_order == "desc"
            options = sorted(
                options,
                key=lambda o: o.get(sort_key, ""),
                reverse=reverse,
            )
        items = [SimpleTerm("", "", "")]
        for opt in options:
            val = opt.get("ResultValue", "")
            txt = opt.get("ResultText", "")
            items.append(SimpleTerm(val, val, txt))
        return SimpleVocabulary(items)


# Factory instances for ZCML registration
AnalysisMethodsVocabularyFactory = AnalysisMethodsVocabulary()
AnalysisInstrumentsVocabularyFactory = (
    AnalysisInstrumentsVocabulary()
)
AnalysisAnalystsVocabularyFactory = (
    AnalysisAnalystsVocabulary()
)
AnalysisUnitsVocabularyFactory = AnalysisUnitsVocabulary()
AnalysisDLOperandsVocabularyFactory = (
    AnalysisDLOperandsVocabulary()
)
AnalysisResultOptionsVocabularyFactory = (
    AnalysisResultOptionsVocabulary()
)
