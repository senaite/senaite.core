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

"""Hazard pictogram helpers (GHS + ISO 7010)."""

from bika.lims import senaiteMessageFactory as _
from senaite.core.api import get_attr
from senaite.core.api import get_portal_url
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.i18n import translate
from senaite.core.vocabularies.hazard_categories import format_title
from senaite.core.vocabularies.hazard_categories import get_category

PICTOGRAM_PATH = (
    "/++plone++senaite.core.static/images/{pictogram}")
WARNING_PICTOGRAM_PATH = (
    "/++plone++senaite.core.static/images/iso/W001.svg")
WARNING_LABEL = _(u"hazard_warning_label", default=u"Hazardous")


def get_pictogram_url(code):
    """Get the absolute URL of the hazard pictogram for a category code

    Resolves both GHS and ISO 7010 hazard category codes.

    :param code: Hazard category code (e.g. `"GHS01"` or `"BIO01"`)
    :type code: str
    :returns: Absolute URL of the pictogram SVG, or empty string when
              the code is unknown
    :rtype: str
    """
    category = get_category(code)
    if not category:
        return u""
    return get_portal_url() + PICTOGRAM_PATH.format(
        pictogram=category["pictogram"])


def get_warning_pictogram_url():
    """Get the absolute URL of the ISO 7010 W001 'General warning' SVG

    Used as the fallback pictogram when a sample is marked hazardous
    but no specific hazard category has been assigned.

    :returns: Absolute URL of the W001 SVG
    :rtype: str
    """
    return get_portal_url() + WARNING_PICTOGRAM_PATH


def get_pictogram(code):
    """Get a view-model dict for a single hazard category

    :param code: Hazard category code (e.g. `"GHS01"` or `"BIO01"`)
    :type code: str
    :returns: `{"code": code, "url": ..., "alt": ..., "title": ...}`
              or `None` when the code is unknown.
    :rtype: dict or None
    """
    category = get_category(code)
    if not category:
        return None
    return {
        "code": code,
        "url": get_pictogram_url(code),
        "alt": code,
        "title": format_title(category),
    }


def get_pictograms_for_codes(codes, hazardous=True):
    """Get pictogram view-models for a list of hazard category codes

    Empty list when `hazardous` is false. When `hazardous` is true
    but `codes` is empty, returns a single ISO 7010 W001 'General
    warning' fallback. Suitable for callers that already have the
    codes (e.g. from a catalog brain) and want to avoid waking the
    sample up.

    :param codes: Hazard category codes
    :type codes: list, tuple, or None
    :param hazardous: Whether the sample is marked hazardous
    :type hazardous: bool
    :returns: List of pictogram view-model dicts
    :rtype: list[dict]
    """
    if not hazardous:
        return []
    codes = list(codes or [])
    if not codes:
        warning = translate(WARNING_LABEL, to_utf8=False)
        return [{
            "code": None,
            "url": get_warning_pictogram_url(),
            "alt": warning,
            "title": warning,
        }]
    pictograms = []
    for code in codes:
        picto = get_pictogram(code)
        if picto is not None:
            pictograms.append(picto)
    return pictograms


def get_pictograms_for_sample(sample):
    """Get hazard pictogram view-models for a sample

    Accepts both a wakened sample object and a catalog brain. The
    sample's hazardous flag and categories are resolved by looking
    up the SampleType brain in the setup catalog (via the
    `getSampleTypeUID` index on the sample), so SampleType edits
    show up in listings without waking samples or reindexing them:

    1. `getCustomHazardCategories` (per-sample override, optional)
       is consulted first when present.
    2. Otherwise both `getHazardous` and `getHazardCategories`
       are read from the SampleType brain metadata.

    :param sample: Sample (AnalysisRequest) or catalog brain
    :returns: List of pictogram view-model dicts
    :rtype: list[dict]
    """
    sample_type_uid = get_attr(sample, "getSampleTypeUID")
    if not sample_type_uid:
        return []
    hazardous = bool(get_attr(
        sample_type_uid, "getHazardous", catalog=SETUP_CATALOG))
    if not hazardous:
        return []
    codes = get_attr(sample, "getCustomHazardCategories") or []
    if not codes:
        codes = get_attr(
            sample_type_uid,
            "getHazardCategories",
            catalog=SETUP_CATALOG) or []
    return get_pictograms_for_codes(list(codes), hazardous=hazardous)


def get_pictograms_for_reference(obj):
    """Get hazard pictogram view-models for a reference object

    Works for any object that carries `getHazardous` and
    `getHazardCategories` accessors (or matching brain metadata
    columns): `ReferenceDefinition` and `ReferenceSample`.
    `get_attr` reads the metadata column on a brain and calls
    the accessor on an object.

    :param obj: ReferenceSample, ReferenceDefinition or brain
    :returns: List of pictogram view-model dicts
    :rtype: list[dict]
    """
    hazardous = bool(get_attr(obj, "getHazardous"))
    if not hazardous:
        return []
    codes = get_attr(obj, "getHazardCategories") or []
    return get_pictograms_for_codes(list(codes), hazardous=hazardous)
