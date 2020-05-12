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
from Products.Archetypes.public import Schema, registerType
from bika.lims import api
from bika.lims import PROJECTNAME
from bika.lims.content.abstractroutineanalysis import AbstractRoutineAnalysis
from bika.lims.content.abstractroutineanalysis import schema
from bika.lims.interfaces import IRoutineAnalysis
from bika.lims.workflow.analysis import STATE_RETRACTED, STATE_REJECTED
from zope.interface import implements

schema = schema.copy() + Schema((

))


class Analysis(AbstractRoutineAnalysis):
    implements(IRoutineAnalysis)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    @security.public
    def getSiblings(self, with_retests=False):
        """
        Returns the list of analyses of the Analysis Request to which this
        analysis belongs to, but with the current analysis excluded.
        :param with_retests: If false, siblings with retests are dismissed
        :type with_retests: bool
        :return: list of siblings for this analysis
        :rtype: list of IAnalysis
        """
        request = self.getRequest()
        if not request:
            return []

        siblings = []
        retracted_states = [STATE_RETRACTED, STATE_REJECTED]
        for sibling in request.getAnalyses(full_objects=True):
            if api.get_uid(sibling) == self.UID():
                # Exclude me from the list
                continue

            if not with_retests:
                if api.get_workflow_status_of(sibling) in retracted_states:
                    # Exclude retracted analyses
                    continue
                elif sibling.getRetest():
                    # Exclude analyses with a retest
                    continue

            siblings.append(sibling)

        return siblings

    def workflow_script_publish(self):
        """
        If this is not here, acquisition causes recursion into
        AR workflow_script_publish method and, if there are enough
        analyses, it will result in "RuntimeError: maximum recursion
        depth exceeded"
        """
        pass

registerType(Analysis, PROJECTNAME)
