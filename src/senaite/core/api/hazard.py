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
from bika.lims.utils import render_html_attributes
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
# Lazy i18n Message; do not treat as a plain string.
WARNING_LABEL = _(u"hazard_warning_label", default=u"Hazardous")

DEFAULT_PICTOGRAM_CLASS = "hazard-pictogram-mini"


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

    The `alt` text uses the translated title so screen readers
    announce the hazard meaning instead of the opaque code.

    :param code: Hazard category code (e.g. `"GHS01"` or `"BIO01"`)
    :type code: str
    :returns: `{"code": code, "url": ..., "alt": ..., "title": ...}`
              or `None` when the code is unknown.
    :rtype: dict or None
    """
    category = get_category(code)
    if not category:
        return None
    title = format_title(category)
    return {
        "code": code,
        "url": get_pictogram_url(code),
        "alt": title,
        "title": title,
    }


def get_pictograms_for_codes(codes, hazardous=True):
    """Get pictogram view-models for a list of hazard category codes

    Empty list when `hazardous` is false. When `hazardous` is true
    but `codes` is empty, returns a single ISO 7010 W001 'General
    warning' fallback (with an empty-string `code` so consumers can
    rely on `code` being a string in all entries).

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
            "code": "",
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


def get_pictograms_for_sample(sample, sample_type_cache=None):
    """Get hazard pictogram view-models for a sample

    Accepts both a wakened sample object and a catalog brain. The
    sample's hazardous flag and categories are resolved from the
    SampleType brain in the setup catalog (looked up by UID via the
    `getSampleTypeUID` FieldIndex), so SampleType edits show up in
    listings without waking samples or reindexing them.

    Pass a fresh `sample_type_cache` dict per request when calling
    this in a listing context. It maps SampleType UID to the
    resolved `(hazardous, codes)` tuple and avoids one setup-catalog
    hit per row when many samples share the same SampleType.

    :param sample: Sample (AnalysisRequest) or catalog brain
    :param sample_type_cache: Optional mutable mapping used to cache
                              SampleType brain lookups by UID
    :returns: List of pictogram view-model dicts
    :rtype: list[dict]
    """
    sample_type_uid = get_attr(sample, "getSampleTypeUID")
    if not sample_type_uid:
        return []
    cache = sample_type_cache if sample_type_cache is not None else {}
    if sample_type_uid in cache:
        hazardous, codes = cache[sample_type_uid]
    else:
        hazardous = bool(get_attr(
            sample_type_uid, "getHazardous", catalog=SETUP_CATALOG))
        codes = get_attr(
            sample_type_uid,
            "getHazardCategories",
            catalog=SETUP_CATALOG) or []
        cache[sample_type_uid] = (hazardous, list(codes))
        codes = cache[sample_type_uid][1]
    return get_pictograms_for_codes(codes, hazardous=hazardous)


def get_pictograms_for_reference(obj):
    """Get hazard pictogram view-models for a reference object

    Works for any object (or brain) that carries `getHazardous` and
    `getHazardCategories` accessors / metadata columns:
    `ReferenceDefinition`, `ReferenceSample` and `SampleType`.
    `get_attr` reads the metadata column on a brain and calls the
    accessor on an object.

    :param obj: ReferenceSample, ReferenceDefinition, SampleType or
                a brain for any of the above
    :returns: List of pictogram view-model dicts
    :rtype: list[dict]
    """
    hazardous = bool(get_attr(obj, "getHazardous"))
    if not hazardous:
        return []
    codes = get_attr(obj, "getHazardCategories") or []
    return get_pictograms_for_codes(codes, hazardous=hazardous)


def render_pictogram_img(picto, css_class=DEFAULT_PICTOGRAM_CLASS):
    """Render a pictogram view-model dict as an HTML `<img>` tag

    Centralizes the markup so the four listing call sites stay
    consistent on attributes, escaping and CSS class.

    :param picto: View-model dict from one of the `get_pictograms_*`
                  helpers
    :param css_class: CSS class for the rendered `<img>` element
    :returns: HTML `<img>` tag as a utf-8 encoded byte string,
              suitable for direct insertion into a listing column
    :rtype: bytes
    """
    attrs = render_html_attributes(
        src=picto["url"],
        alt=picto["alt"],
        title=picto["title"],
        **{"class": css_class})
    return "<img " + attrs + " />"
