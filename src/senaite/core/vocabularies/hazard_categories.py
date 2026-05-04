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
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

# GHS hazard categories defined by UN/ECE.
# See https://unece.org/transport/dangerous-goods/ghs-pictograms.
#
# Each entry holds:
#   - code: the canonical GHS identifier (used as token and stored value)
#   - name: the official category name (translatable)
#   - common: a familiar synonym shown alongside the formal name
#   - pictogram: filename of the SVG under
#                ``senaite.core/browser/static/images/ghs/``
GHS_CATEGORIES = (
    {
        "code": "GHS01",
        "name": _(u"hazard_GHS01_name", default=u"Explosive"),
        "common": _(u"hazard_GHS01_common", default=u"explosive"),
        "pictogram": "GHS01.svg",
    },
    {
        "code": "GHS02",
        "name": _(u"hazard_GHS02_name", default=u"Flammable"),
        "common": _(u"hazard_GHS02_common", default=u"flammable"),
        "pictogram": "GHS02.svg",
    },
    {
        "code": "GHS03",
        "name": _(u"hazard_GHS03_name", default=u"Oxidizing"),
        "common": _(u"hazard_GHS03_common", default=u"oxidizing"),
        "pictogram": "GHS03.svg",
    },
    {
        "code": "GHS04",
        "name": _(u"hazard_GHS04_name", default=u"Compressed gas"),
        "common": _(u"hazard_GHS04_common", default=u"pressurised gas"),
        "pictogram": "GHS04.svg",
    },
    {
        "code": "GHS05",
        "name": _(u"hazard_GHS05_name", default=u"Corrosive"),
        "common": _(u"hazard_GHS05_common", default=u"acid / caustic"),
        "pictogram": "GHS05.svg",
    },
    {
        "code": "GHS06",
        "name": _(u"hazard_GHS06_name", default=u"Acute toxicity"),
        "common": _(u"hazard_GHS06_common", default=u"poisonous"),
        "pictogram": "GHS06.svg",
    },
    {
        "code": "GHS07",
        "name": _(u"hazard_GHS07_name", default=u"Health hazard"),
        "common": _(u"hazard_GHS07_common", default=u"harmful / irritant"),
        "pictogram": "GHS07.svg",
    },
    {
        "code": "GHS08",
        "name": _(u"hazard_GHS08_name", default=u"Serious health hazard"),
        "common": _(u"hazard_GHS08_common",
                    default=u"carcinogenic / mutagenic"),
        "pictogram": "GHS08.svg",
    },
    {
        "code": "GHS09",
        "name": _(u"hazard_GHS09_name", default=u"Environmental hazard"),
        "common": _(u"hazard_GHS09_common", default=u"environmentally hazardous"),
        "pictogram": "GHS09.svg",
    },
)

LABELS_REGISTRY_KEY = "senaite.core.hazard_category_labels"


def get_categories():
    """Return the GHS category list (as defined in code)."""
    return GHS_CATEGORIES


def get_overridden_labels():
    """Return the per-code label overrides from the registry.

    Format: {"GHS01": u"Explosivstoff", ...}.
    """
    overrides = api.get_registry_record(
        LABELS_REGISTRY_KEY, default=None) or {}
    return overrides


def get_category(code):
    """Return the category dict for ``code`` or ``None``."""
    for category in GHS_CATEGORIES:
        if category["code"] == code:
            return category
    return None


def format_title(category, overrides=None):
    """Return ``"GHSxx - Name (common)"``, honoring overrides."""
    overrides = overrides or {}
    code = category["code"]
    name = overrides.get(code) or api.translate(category["name"])
    common = api.translate(category["common"])
    if common:
        return u"{} - {} ({})".format(code, name, common)
    return u"{} - {}".format(code, name)


@implementer(IVocabularyFactory)
class HazardCategoriesVocabulary(object):
    """Vocabulary of GHS hazard categories.

    Tokens and stored values are the GHS codes (``GHS01`` ... ``GHS09``),
    so changes to translations and labels do not affect persistence.
    """

    def __call__(self, context):
        overrides = get_overridden_labels()
        terms = [
            SimpleTerm(
                value=category["code"],
                token=category["code"],
                title=format_title(category, overrides),
            )
            for category in GHS_CATEGORIES
        ]
        return SimpleVocabulary(terms)


HazardCategoriesVocabularyFactory = HazardCategoriesVocabulary()
