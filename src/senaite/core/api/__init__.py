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

from bika.lims import senaiteMessageFactory as _
from senaite.core.vocabularies.hazard_categories import format_title
from senaite.core.vocabularies.hazard_categories import get_category
from senaite.core.vocabularies.hazard_categories import get_overridden_labels
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.i18n import translate as zope_translate

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


def translate(message, context=None):
    """Translate an i18n message using the current request locale

    :param message: Message to translate
    :param context: Request used to resolve the locale. When ``None``
                    the current global request is used.
    :returns: Translated string, or the message default when no
              translation is available
    :rtype: unicode
    """
    if context is None:
        context = getRequest()
    return zope_translate(message, context=context)


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


def get_pictogram(code, overrides=None):
    """Get a view-model dict for a single GHS category

    :param code: GHS category code (e.g. ``"GHS01"``)
    :type code: str
    :param overrides: Optional mapping of code -> label override. When
                      ``None`` the registry overrides are looked up
                      automatically.
    :type overrides: dict or None
    :returns: ``{"code": code, "url": ..., "alt": ..., "title": ...}``
              or ``None`` when the code is unknown.
    :rtype: dict or None
    """
    category = get_category(code)
    if not category:
        return None
    if overrides is None:
        overrides = get_overridden_labels()
    return {
        "code": code,
        "url": get_pictogram_url(code),
        "alt": code,
        "title": format_title(category, overrides),
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
        warning = translate(WARNING_LABEL)
        return [{
            "code": None,
            "url": get_warning_pictogram_url(),
            "alt": warning,
            "title": warning,
        }]
    overrides = get_overridden_labels()
    pictograms = []
    for code in codes:
        picto = get_pictogram(code, overrides=overrides)
        if picto is not None:
            pictograms.append(picto)
    return pictograms


def get_pictograms_for_sample(sample):
    """Get pictogram view-models for a sample

    Wakes the sample up. For listings that already iterate over
    catalog brains, prefer :func:`get_pictograms_for_codes` with the
    brain metadata.

    :param sample: Sample (AnalysisRequest) to read from
    :returns: List of pictogram view-model dicts
    :rtype: list[dict]
    """
    return get_pictograms_for_codes(
        sample.getHazardCategories(),
        hazardous=sample.getHazardous())
