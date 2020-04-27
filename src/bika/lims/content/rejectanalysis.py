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

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import ReferenceField, Schema, registerType
from bika.lims.content.analysis import Analysis
from bika.lims.config import PROJECTNAME
from bika.lims.content.analysis import schema as analysis_schema
from bika.lims.interfaces import IRejectAnalysis
from zope.interface import implements

schema = analysis_schema + Schema((
    # The analysis that was originally rejected
    ReferenceField(
        'Analysis',
        allowed_types=('Analysis',),
        relationship='RejectAnalysisAnalysis',
    ),
))


class RejectAnalysis(Analysis):
    implements(IRejectAnalysis)
    security = ClassSecurityInfo()

    schema = schema

    @security.public
    def getSample(self):
        return self.aq_parent


registerType(RejectAnalysis, PROJECTNAME)
