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

from collections import OrderedDict

from bika.lims import _
from bika.lims import api
from senaite.core.api import geo
from senaite.core.config.setup import SKIP_NAV_TYPES
from senaite.core.interfaces import IWorksheetLayouts
from zope.component import getUtilitiesFor
from zope.i18n.locales import locales
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


ANALYSIS_COLUMNS = OrderedDict([
    ("created", u"Date Created"),
    ("Service", u"Analysis"),
    ("AdditionalValues", u"Additional Values"),
    ("DetectionLimitOperand", u"DL"),
    ("Result", u"Result"),
    ("Uncertainty", u"+-"),
    ("Unit", u"Unit"),
    ("Specification", u"Specification"),
    ("retested", u"Retested"),
    ("Method", u"Method"),
    ("Instrument", u"Instrument"),
    ("Calculation", u"Calculation"),
    ("Attachments", u"Attachments"),
    ("SubmittedBy", u"Submitter"),
    ("Analyst", u"Analyst"),
    ("ResultCaptureDate", u"Captured"),
    ("DueDate", u"Due Date"),
    ("state_title", u"Status"),
    ("Hidden", u"Hidden"),
])

WORKSHEET_ANALYSIS_COLUMNS = OrderedDict([
    ("Pos", u"Position"),
    ("Service", u"Analysis"),
    ("AdditionalValues", u"Additional Values"),
    ("DetectionLimitOperand", u"DL"),
    ("Result", u"Result"),
    ("Uncertainty", u"+-"),
    ("Unit", u"Unit"),
    ("Specification", u"Specification"),
    ("retested", u"Retested"),
    ("Method", u"Method"),
    ("Instrument", u"Instrument"),
    ("Calculation", u"Calculation"),
    ("Attachments", u"Attachments"),
    ("SubmittedBy", u"Submitter"),
    ("Analyst", u"Analyst"),
    ("ResultCaptureDate", u"Captured"),
    ("DueDate", u"Due Date"),
    ("state_title", u"Status"),
    ("Hidden", u"Hidden"),
])


@implementer(IVocabularyFactory)
class CurrenciesVocabulary(object):
    """Vocabulary of currencies
    """

    def __call__(self, context):
        locale = locales.getLocale("en", "US")
        currencies = locale.numbers.currencies.values()
        items = [(c.type, c.type, u"{} ({})".format(c.displayName, c.symbol))
                 for c in currencies]
        items.sort(key=lambda x: x[2])
        return SimpleVocabulary.fromItems(items)


@implementer(IVocabularyFactory)
class CountriesVocabulary(object):
    """Vocabulary of countries
    """

    def __call__(self, context):
        countries = geo.get_countries()
        items = [(country.alpha_2, country.alpha_2, country.name)
                 for country in countries]
        return SimpleVocabulary.fromItems(items)


@implementer(IVocabularyFactory)
class DecimalMarksVocabulary(object):
    """Vocabulary of decimal marks
    """

    def __call__(self, context):
        items = [
            (".", ".", _(u"Dot (.)")),
            (",", ",", _(u"Comma (,)")),
        ]
        return SimpleVocabulary.fromItems(items)


@implementer(IVocabularyFactory)
class ScientificNotationVocabulary(object):
    """Vocabulary of scientific notation options
    """

    def __call__(self, context):
        items = [
            ("1", "1", u"aE+b / aE-b"),
            ("2", "2", u"ax10^b / ax10^-b"),
            ("3", "3", u"ax10^b / ax10^-b (with superscript)"),
            ("4", "4", u"a·10^b / a·10^-b"),
            ("5", "5", u"a·10^b / a·10^-b (with superscript)"),
        ]
        return SimpleVocabulary.fromItems(items)


@implementer(IVocabularyFactory)
class WorksheetLayoutVocabulary(object):
    """Vocabulary of worksheet layout options
    """

    def __call__(self, context=None):
        layouts = []
        for name, utility in getUtilitiesFor(IWorksheetLayouts):
            items = utility.getResultLayouts()
            [layouts.append((key, key, title)) for key, title in items]

        return SimpleVocabulary.fromItems(layouts)


@implementer(IVocabularyFactory)
class WeekdaysVocabulary(object):
    """Vocabulary of weekdays
    """

    def __call__(self, context):
        items = [
            ("0", "0", _(u"Monday")),
            ("1", "1", _(u"Tuesday")),
            ("2", "2", _(u"Wednesday")),
            ("3", "3", _(u"Thursday")),
            ("4", "4", _(u"Friday")),
            ("5", "5", _(u"Saturday")),
            ("6", "6", _(u"Sunday")),
        ]
        return SimpleVocabulary.fromItems(items)


@implementer(IVocabularyFactory)
class MultiVerificationTypeVocabulary(object):
    """Vocabulary of multi-verification types
    """

    def __call__(self, context):
        items = [
            ("self_multi_enabled", "self_multi_enabled",
             _(u"Allow same user to verify multiple times")),
            ("self_multi_not_cons", "self_multi_not_cons",
             _(u"Allow same user to verify multiple times, "
               u"but not consecutively")),
            ("self_multi_disabled", "self_multi_disabled",
             _(u"Disable multi-verification for the same user")),
        ]
        return SimpleVocabulary.fromItems(items)


@implementer(IVocabularyFactory)
class NumberOfVerificationsVocabulary(object):
    """Vocabulary for number of required verifications
    """

    def __call__(self, context):
        items = [(1, 1, u"1"), (2, 2, u"2"), (3, 3, u"3"), (4, 4, u"4")]
        return SimpleVocabulary.fromItems(items)


@implementer(IVocabularyFactory)
class TopLevelFoldersVocabulary(object):
    """Vocabulary of top-level folders in the portal
    """

    def __call__(self, context):
        portal = api.get_portal()
        items = []

        # Get all immediate children of portal
        for obj_id in portal.objectIds():
            obj = portal[obj_id]
            # Check if object is AT or DX
            if not api.is_object(obj):
                continue
            if api.get_portal_type(obj) in SKIP_NAV_TYPES:
                continue
            # Get title and id
            title = api.get_title(obj)
            items.append((obj_id, obj_id, title))

        # Sort by title
        items.sort(key=lambda x: x[2])
        return SimpleVocabulary.fromItems(items)


@implementer(IVocabularyFactory)
class NavigationPortalTypesVocabulary(object):
    """Vocabulary of portal types with friendly names for navigation
    """

    def __call__(self, context):
        portal_types = api.get_tool("portal_types")
        items = []

        # Get all portal types
        for portal_type in portal_types.objectIds():
            if portal_type in SKIP_NAV_TYPES:
                continue
            fti = portal_types.getTypeInfo(portal_type)
            if fti:
                title = portal_type
                items.append((portal_type, portal_type, title))

        # Sort by title
        items.sort(key=lambda x: x[2])
        return SimpleVocabulary.fromItems(items)


@implementer(IVocabularyFactory)
class AnalysisColumnsVocabulary(object):
    """Vocabulary of analysis column keys with titles
    """

    def __call__(self, context):
        items = [
            (key, key, title)
            for key, title in ANALYSIS_COLUMNS.items()
        ]
        return SimpleVocabulary.fromItems(items)


@implementer(IVocabularyFactory)
class WorksheetAnalysisColumnsVocabulary(object):
    """Vocabulary of worksheet analysis column keys
    """

    def __call__(self, context):
        items = [
            (key, key, title)
            for key, title
            in WORKSHEET_ANALYSIS_COLUMNS.items()
        ]
        return SimpleVocabulary.fromItems(items)


# Factory instances
CurrenciesVocabularyFactory = CurrenciesVocabulary()
CountriesVocabularyFactory = CountriesVocabulary()
DecimalMarksVocabularyFactory = DecimalMarksVocabulary()
ScientificNotationVocabularyFactory = ScientificNotationVocabulary()
WorksheetLayoutVocabularyFactory = WorksheetLayoutVocabulary()
WeekdaysVocabularyFactory = WeekdaysVocabulary()
MultiVerificationTypeVocabularyFactory = MultiVerificationTypeVocabulary()
NumberOfVerificationsVocabularyFactory = NumberOfVerificationsVocabulary()
TopLevelFoldersVocabularyFactory = TopLevelFoldersVocabulary()
NavigationPortalTypesVocabularyFactory = NavigationPortalTypesVocabulary()
AnalysisColumnsVocabularyFactory = AnalysisColumnsVocabulary()
WorksheetAnalysisColumnsVocabularyFactory = (
    WorksheetAnalysisColumnsVocabulary()
)
