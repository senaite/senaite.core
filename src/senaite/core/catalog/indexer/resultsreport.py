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
from plone.indexer import indexer
from senaite.core.interfaces import IResultsReport


@indexer(IResultsReport)
def sample_uid(instance):
    """Returns a list of UIDs of the contained Samples
    """
    return instance.getRawContainedAnalysisRequests()


@indexer(IResultsReport)
def resultsreport_searchable_text(instance):
    """Searchable text for ResultsReport
    """
    sample = instance.getAnalysisRequest()
    if not sample:
        return u""

    # Metadata is a plain dict (same as AT version)
    metadata = instance.getMetadata() or {}

    tokens = [
        sample.getId(),
        sample.getBatchID() or "",
        metadata.get("paperformat", ""),
        metadata.get("orientation", ""),
        metadata.get("template", ""),
    ]

    # Extend IDs of contained Samples
    contained_samples = instance.getContainedAnalysisRequests()
    tokens.extend([api.get_id(s) for s in contained_samples if s])

    # Extend email recipients
    recipients = []
    send_log = instance.getSendLog() or []
    for log in send_log:
        email_recipients = log.get("email_recipients", [])
        if email_recipients:
            recipients.extend(email_recipients)

    tokens.extend(recipients)

    # Filter out None/empty values and convert to unicode
    tokens = [api.safe_unicode(t) for t in tokens if t]

    return u" ".join(list(set(tokens)))
