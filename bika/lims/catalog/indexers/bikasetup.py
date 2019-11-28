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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from plone.indexer import indexer

from bika.lims.interfaces import IBikaSetupCatalog
from bika.lims.interfaces import ISampleTypeAwareMixin


@indexer(ISampleTypeAwareMixin, IBikaSetupCatalog)
def sampletype_uids(instance):
    """Returns the list of SampleType UIDs the instance is assigned to

    This is a KeywordIndex, so it will be indexed as a list, even if only one
    SampleType can be assigned to the instance. Moreover, if the instance has no
    SampleType assigned, it returns a tuple with a None value. This allows
    searches for `MissingValue` entries too.
    """
    return instance.getSampleTypeUID() or (None, )
