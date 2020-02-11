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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from zope.component import adapts

from bika.lims import api
from bika.lims.interfaces import IAddSampleObjectInfo


class AddSampleObjectInfoAdapter(object):
    """Base implementation of an adapter for reference fields used in Sample
    Add form
    """
    adapts(IAddSampleObjectInfo)

    def __init__(self, context):
        self.context = context

    def get_base_info(self):
        """Returns the basic dictionary structure for the current object
        """
        return {
            "id": api.get_id(self.context),
            "uid": api.get_uid(self.context),
            "title": api.get_title(self.context),
            "field_values": {},
            "filter_queries": {},
        }

    def get_object_info(self):
        """Returns the dict representation of the context object for its
        correct consumption by Sample Add form.
        See IAddSampleObjectInfo for further details
        """
        raise NotImplementedError("get_object_info not implemented")
