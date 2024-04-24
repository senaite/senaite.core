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
from plone.indexer import indexer
from senaite.core.interfaces import ISamplePoint
from senaite.core.interfaces import ISetupCatalog


@indexer(ISamplePoint, ISetupCatalog)
def sampletype_title(instance):
    """Returns a list of titles from SampleType the instance is assigned to
    If the instance has no sample type assigned, it returns a tuple with an
    empty value. This allows searches for `MissingValue` entries too.
    """
    sample_type = instance.getSampleTypes()
    return map(api.get_title, sample_type) or [""]


@indexer(ISamplePoint, ISetupCatalog)
def sampletype_uid(instance):
    """Returns a list of uids from SampleType the instance is assigned to
    If the instance has no SampleType assigned, it returns a tuple with an
    empty value. This allows searches for `MissingValue` entries too.
    """
    return instance.getRawSampleTypes() or [""]
