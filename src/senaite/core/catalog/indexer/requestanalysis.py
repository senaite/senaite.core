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

from datetime import datetime
from datetime import timedelta

from bika.lims import api
from bika.lims.interfaces.analysis import IRequestAnalysis
from plone.indexer import indexer
from senaite.core.api import dtime


@indexer(IRequestAnalysis)
def getAncestorsUIDs(instance):
    """Returns the UIDs of all the ancestors (Analysis Requests) this analysis
    comes from
    """
    request = instance.getRequest()
    parents = map(lambda ar: api.get_uid(ar), request.getAncestors())
    return [api.get_uid(request)] + parents


@indexer(IRequestAnalysis)
def sortable_due_date(instance):
    """Returns the due date of the analysis, but without taking workdays into
    account. This is a hint for sorting by due date, but it's value might not
    match with the real due date.
    """
    tat = instance.getMaxTimeAllowed()
    if not tat:
        return dtime.to_DT(datetime.max)

    start = instance.getStartProcessDate()
    if not start:
        return dtime.to_DT(datetime.max)

    start = dtime.to_dt(start)
    tat = api.to_minutes(**tat)
    due_date = start + timedelta(minutes=tat)
    return dtime.to_DT(due_date)
