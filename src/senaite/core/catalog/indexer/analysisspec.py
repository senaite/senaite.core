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
from bika.lims.interfaces import IAnalysisSpec
from plone.indexer import indexer
from senaite.core.interfaces import ISetupCatalog


@indexer(IAnalysisSpec, ISetupCatalog)
def sampletype_title(instance):
    """Returns a list containing the title of the sample type assigned to this
    instance, as defined by the AnalysisSpec type. The function returns a list
    because the index used is a KeywordIndex, which supports searching for
    missing values in cases where the sample type is not a mandatory field.
    """
    sample_type = instance.getSampleType()
    if not sample_type:
        return [""]
    return [api.get_title(sample_type)]


@indexer(IAnalysisSpec, ISetupCatalog)
def sampletype_uid(instance):
    """Returns a list containing the UID of the sample type assigned to this
    instance, as defined by the AnalysisSpec type. The function returns a list
    because the index used is a KeywordIndex, which supports searching for
    missing values in cases where the sample type is not a mandatory field.
    """
    uid = instance.getRawSampleType()
    if not uid:
        return [""]
    return [uid]
