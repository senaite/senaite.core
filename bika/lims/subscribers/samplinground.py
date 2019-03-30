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

from bika.lims.idserver import renameAfterCreation

def SamplingRoundAddedEventHandler(instance, event):
    """ Event fired when BikaSetup object gets modified.
        Since Sampling Round is a dexterity object we have to change the ID by "hand"
        Then we have to redirect the user to the ar add form
    """
    if instance.portal_type != "SamplingRound":
        print("How does this happen: type is %s should be SamplingRound" % instance.portal_type)
        return
    renameAfterCreation(instance)
    num_art = len(instance.ar_templates)
    destination_url = instance.aq_parent.absolute_url() + \
                    "/portal_factory/" + \
                    "AnalysisRequest/Request new analyses/ar_add?samplinground=" + \
                    instance.UID() + "&ar_count=" + str(num_art)
    request = getattr(instance, 'REQUEST', None)
    request.response.redirect(destination_url)
