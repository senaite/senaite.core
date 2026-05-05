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

"""Public helper API for SENAITE.

Functions exposed here form the senaite.core.api namespace. Use
``from senaite.core import api`` and then ``api.get_portal_url()``,
mirroring the long-standing ``bika.lims.api`` module that this package
will gradually replace.
"""

from bika.lims import api as _bika_api
from bika.lims import senaiteMessageFactory as _
from Products.CMFPlone.utils import safe_callable
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.i18n import translate
from senaite.core.vocabularies.hazard_categories import format_title
from senaite.core.vocabularies.hazard_categories import get_category
from zope.component.hooks import getSite

GHS_PICTOGRAM_PATH = (
    "/++plone++senaite.core.static/images/ghs/{pictogram}")
WARNING_PICTOGRAM_PATH = (
    "/++plone++senaite.core.static/images/iso/W001.svg")
WARNING_LABEL = _(u"hazard_warning_label", default=u"Hazardous")


def get_portal():
    """Get the portal object

    :returns: Portal object
    """
    return getSite()


def get_portal_url():
    """Get the absolute URL of the portal

    :returns: Absolute portal URL
    :rtype: str
    """
    return get_portal().absolute_url()


def get_pictogram_url(code):
    """Get the absolute URL of the GHS pictogram for a category code

    :param code: GHS category code (e.g. ``"GHS01"``)
    :type code: str
    :returns: Absolute URL of the pictogram SVG, or empty string when
              the code is unknown
    :rtype: str
    """
    category = get_category(code)
    if not category:
        return u""
    return get_portal_url() + GHS_PICTOGRAM_PATH.format(
        pictogram=category["pictogram"])


def get_warning_pictogram_url():
    """Get the absolute URL of the ISO 7010 W001 'General warning' SVG

    Used as the fallback pictogram when a sample is marked hazardous
    but no specific GHS category has been assigned.

    :returns: Absolute URL of the W001 SVG
    :rtype: str
    """
    return get_portal_url() + WARNING_PICTOGRAM_PATH


def get_pictogram(code):
    """Get a view-model dict for a single GHS category

    :param code: GHS category code (e.g. ``"GHS01"``)
    :type code: str
    :returns: ``{"code": code, "url": ..., "alt": ..., "title": ...}``
              or ``None`` when the code is unknown.
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
    """Get pictogram view-models for a list of GHS category codes

    Empty list when ``hazardous`` is false. When ``hazardous`` is true
    but ``codes`` is empty, returns a single ISO 7010 W001 'General
    warning' fallback. Suitable for callers that already have the
    codes (e.g. from a catalog brain) and want to avoid waking the
    sample up.

    :param codes: GHS category codes
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


def get_attr(obj, name, default=None, catalog=None):
    """Return an attribute from an object, brain or UID.

    Accepts any of the three forms ``bika.lims.api.get_uid`` handles:
    a content object, a catalog brain or a UID string. When
    ``catalog`` is given the input is normalized to a brain via a
    UID lookup in that catalog before reading the attribute, which
    avoids waking the object up. Without ``catalog``, the input is
    read directly: a method is called, a bare attribute is returned
    as-is.

    Uses ``Products.CMFPlone.utils.safe_callable`` so a transient
    ConflictError in the callable check is not swallowed.

    :param obj: Content object, catalog brain or UID
    :param name: Attribute or method name
    :param default: Value returned when ``obj`` is empty, the
                    attribute is missing, the catalog lookup yields
                    no brain, or the call raises ``TypeError``
    :param catalog: Catalog id or tool. When given, ``obj`` is
                    normalized to a brain via UID lookup before
                    reading the attribute.
    :returns: Attribute value (or call result) or ``default``
    """
    if obj is None:
        return default
    if catalog is not None:
        if not (_bika_api.is_object(obj) or _bika_api.is_uid(obj)):
            return default
        uid = _bika_api.get_uid(obj)
        if not uid:
            return default
        brains = _bika_api.search({"UID": uid}, catalog=catalog)
        if not brains:
            return default
        obj = brains[0]
    value = getattr(obj, name, default)
    if safe_callable(value):
        try:
            return value()
        except TypeError:
            return default
    return value


def get_pictograms_for_sample(sample):
    """Get pictogram view-models for a sample

    Accepts both a wakened sample object and a catalog brain. The
    sample's hazard categories are resolved without waking the
    sample type up:

    1. ``getCustomHazardCategories`` (per-sample override, optional)
       is consulted first when present.
    2. Otherwise the SampleType is looked up by its UID in the setup
       catalog and ``getHazardCategories`` is read from its brain
       metadata.

    :param sample: Sample (AnalysisRequest) or catalog brain
    :returns: List of pictogram view-model dicts
    :rtype: list[dict]
    """
    hazardous = bool(get_attr(sample, "getHazardous"))
    if not hazardous:
        return []
    codes = get_attr(sample, "getCustomHazardCategories") or []
    if not codes:
        codes = get_attr(
            get_attr(sample, "getSampleTypeUID"),
            "getHazardCategories",
            catalog=SETUP_CATALOG) or []
    return get_pictograms_for_codes(list(codes), hazardous=hazardous)
