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
``from senaite.core import api`` and then ``api.get_pictogram_url(...)``,
mirroring the long-standing ``bika.lims.api`` module that this package
will gradually replace.
"""

from bika.lims import api as _lims_api
from senaite.core.vocabularies.hazard_categories import format_title
from senaite.core.vocabularies.hazard_categories import get_category
from senaite.core.vocabularies.hazard_categories import get_overridden_labels

GHS_PICTOGRAM_PATH = (
    "/++plone++senaite.core.static/images/ghs/{pictogram}")
WARNING_PICTOGRAM_PATH = (
    "/++plone++senaite.core.static/images/iso/W001.svg")
WARNING_LABEL = u"Hazardous"


def _portal_url(portal=None):
    """Return the absolute portal URL.

    Accepts an optional portal so callers that already have a
    handle can avoid the lookup.
    """
    if portal is None:
        portal = _lims_api.get_portal()
    return portal.absolute_url()


def get_pictogram_url(code, portal=None):
    """Return the absolute URL of the pictogram SVG for a GHS code.

    Returns an empty string when the code is unknown.
    """
    category = get_category(code)
    if not category:
        return u""
    return _portal_url(portal) + GHS_PICTOGRAM_PATH.format(
        pictogram=category["pictogram"])


def get_warning_pictogram_url(portal=None):
    """Return the absolute URL of the ISO 7010 W001 SVG fallback."""
    return _portal_url(portal) + WARNING_PICTOGRAM_PATH


def get_pictogram(code, overrides=None, portal=None):
    """Return a view-model dict for a single GHS category.

    Format: ``{"code": GHS01, "url": ..., "alt": GHS01,
    "title": "GHS01 - Name (synonym)"}``.
    """
    category = get_category(code)
    if not category:
        return None
    if overrides is None:
        overrides = get_overridden_labels()
    return {
        "code": code,
        "url": get_pictogram_url(code, portal=portal),
        "alt": code,
        "title": format_title(category, overrides),
    }


def get_pictograms_for_codes(codes, hazardous=True, portal=None):
    """Return the pictogram view-models for a list of GHS codes.

    Empty list when ``hazardous`` is false. When ``hazardous`` is
    true but ``codes`` is empty, returns a single ISO 7010 W001
    'General warning' fallback. Useful for callers that already
    have the codes (e.g. from a catalog brain) and want to avoid
    waking the sample up.
    """
    if not hazardous:
        return []
    if portal is None:
        portal = _lims_api.get_portal()
    codes = list(codes or [])
    if not codes:
        return [{
            "code": None,
            "url": get_warning_pictogram_url(portal=portal),
            "alt": WARNING_LABEL,
            "title": WARNING_LABEL,
        }]
    overrides = get_overridden_labels()
    pictograms = []
    for code in codes:
        picto = get_pictogram(code, overrides=overrides, portal=portal)
        if picto is not None:
            pictograms.append(picto)
    return pictograms


def get_pictograms_for_sample(sample):
    """Return the pictogram view-models that apply to a sample.

    Wakes the sample up. For listings that already iterate over
    catalog brains, prefer :func:`get_pictograms_for_codes` with
    the brain metadata.
    """
    return get_pictograms_for_codes(
        sample.getHazardCategories(),
        hazardous=sample.getHazardous())
