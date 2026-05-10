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

# Hazard / handling categories.
#
# The first 9 entries are the GHS pictograms defined by UN/ECE
# (see https://unece.org/transport/dangerous-goods/ghs-pictograms).
# The remaining entries cover hazard / handling cases that GHS does not
# address (biohazard, radioactive, cold-chain). Custom codes are used
# for the non-GHS entries to avoid clashing with GHS or ISO 7010
# warning-sign codes.
#
# Each entry holds:
#   - code: canonical identifier (used as token and stored value)
#   - name: the official category name (translatable)
#   - common: a familiar synonym shown alongside the formal name
#   - pictogram: path of the SVG relative to
#                ``senaite.core/browser/static/images/``
GHS_CATEGORIES = (
    {
        "code": "GHS01",
        "name": _(u"hazard_GHS01_name", default=u"Explosive"),
        "common": _(u"hazard_GHS01_common", default=u"explosive"),
        "pictogram": "ghs/GHS01.svg",
    },
    {
        "code": "GHS02",
        "name": _(u"hazard_GHS02_name", default=u"Flammable"),
        "common": _(u"hazard_GHS02_common", default=u"flammable"),
        "pictogram": "ghs/GHS02.svg",
    },
    {
        "code": "GHS03",
        "name": _(u"hazard_GHS03_name", default=u"Oxidizing"),
        "common": _(u"hazard_GHS03_common", default=u"oxidizing"),
        "pictogram": "ghs/GHS03.svg",
    },
    {
        "code": "GHS04",
        "name": _(u"hazard_GHS04_name", default=u"Compressed gas"),
        "common": _(u"hazard_GHS04_common", default=u"pressurised gas"),
        "pictogram": "ghs/GHS04.svg",
    },
    {
        "code": "GHS05",
        "name": _(u"hazard_GHS05_name", default=u"Corrosive"),
        "common": _(u"hazard_GHS05_common", default=u"acid / caustic"),
        "pictogram": "ghs/GHS05.svg",
    },
    {
        "code": "GHS06",
        "name": _(u"hazard_GHS06_name", default=u"Acute toxicity"),
        "common": _(u"hazard_GHS06_common", default=u"poisonous"),
        "pictogram": "ghs/GHS06.svg",
    },
    {
        "code": "GHS07",
        "name": _(u"hazard_GHS07_name", default=u"Health hazard"),
        "common": _(u"hazard_GHS07_common", default=u"harmful / irritant"),
        "pictogram": "ghs/GHS07.svg",
    },
    {
        "code": "GHS08",
        "name": _(u"hazard_GHS08_name", default=u"Serious health hazard"),
        "common": _(u"hazard_GHS08_common",
                    default=u"carcinogenic / mutagenic"),
        "pictogram": "ghs/GHS08.svg",
    },
    {
        "code": "GHS09",
        "name": _(u"hazard_GHS09_name", default=u"Environmental hazard"),
        "common": _(u"hazard_GHS09_common", default=u"environmentally hazardous"),
        "pictogram": "ghs/GHS09.svg",
    },
    {
        "code": "BIO01",
        "name": _(u"hazard_BIO01_name", default=u"Biohazard"),
        "common": _(u"hazard_BIO01_common",
                    default=u"infectious / biological"),
        "pictogram": "iso/W009.svg",
    },
    {
        "code": "RAD01",
        "name": _(u"hazard_RAD01_name", default=u"Radioactive"),
        "common": _(u"hazard_RAD01_common", default=u"ionising radiation"),
        "pictogram": "iso/W003.svg",
    },
    {
        "code": "NIR01",
        "name": _(u"hazard_NIR01_name", default=u"Non-ionising radiation"),
        "common": _(u"hazard_NIR01_common",
                    default=u"UV / laser / RF"),
        "pictogram": "iso/W005.svg",
    },
    {
        "code": "ELEC01",
        "name": _(u"hazard_ELEC01_name", default=u"Electricity"),
        "common": _(u"hazard_ELEC01_common", default=u"electric shock"),
        "pictogram": "iso/W012.svg",
    },
    {
        "code": "COLD01",
        "name": _(u"hazard_COLD01_name", default=u"Low temperature"),
        "common": _(u"hazard_COLD01_common",
                    default=u"freezing / cold storage"),
        "pictogram": "iso/W010.svg",
    },
    {
        "code": "HOT01",
        "name": _(u"hazard_HOT01_name", default=u"Hot content"),
        "common": _(u"hazard_HOT01_common", default=u"heated material"),
        "pictogram": "iso/W079.svg",
    },
)

def get_categories():
    """Return the hazard category list (as defined in code)."""
    return GHS_CATEGORIES


def get_category(code):
    """Return the category dict for ``code`` or ``None``."""
    for category in GHS_CATEGORIES:
        if category["code"] == code:
            return category
    return None


def format_title(category):
    """Return ``"<code> - Name (common)"`` as unicode."""
    code = category["code"]
    name = api.safe_unicode(api.translate(category["name"]))
    common = api.safe_unicode(api.translate(category["common"]))
    if common:
        return u"{} - {} ({})".format(code, name, common)
    return u"{} - {}".format(code, name)


@implementer(IVocabularyFactory)
class HazardCategoriesVocabulary(object):
    """Vocabulary of hazard / handling categories.

    Tokens and stored values are short codes — the 9 GHS codes plus
    additional codes for ISO 7010 pictograms (``BIO01``, ``RAD01``,
    ``NIR01``, ``ELEC01``, ``COLD01``) — so changes to translations
    do not affect persistence.
    """

    def __call__(self, context):
        terms = [
            SimpleTerm(
                value=category["code"],
                token=category["code"],
                title=format_title(category),
            )
            for category in GHS_CATEGORIES
        ]
        return SimpleVocabulary(terms)


HazardCategoriesVocabularyFactory = HazardCategoriesVocabulary()
