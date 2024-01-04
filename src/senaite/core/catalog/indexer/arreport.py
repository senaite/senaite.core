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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims.interfaces import IARReport
from plone.indexer import indexer


@indexer(IARReport)
def sample_uid(instance):
    """Returns a list of UIDs of the contained Samples
    """
    return instance.getRawContainedAnalysisRequests()


@indexer(IARReport)
def arreport_searchable_text(instance):
    sample = instance.getAnalysisRequest()
    metadata = instance.getMetadata() or {}

    tokens = [
        sample.getId(),
        sample.getBatchID(),
        metadata.get("paperformat", ""),
        metadata.get("orientation", ""),
        metadata.get("template", ""),
    ]

    # Extend IDs of contained Samples
    contained_samples = instance.getContainedAnalysisRequests()
    tokens.extend(map(api.get_id, contained_samples))

    # Extend email recipients
    recipients = []
    for log in instance.getSendLog():
        for recipient in log.get("email_recipients", []):
            recipients.append(recipient)

    tokens.extend(recipients)

    return u" ".join(list(set(tokens)))
