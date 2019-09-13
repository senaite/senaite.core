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


def SamplingRoundAddedEventHandler(instance, event):
    """Redirect user to the sample add form
    """
    if instance.portal_type != "SamplingRound":
        raise TypeError("Expected portal type 'SamplingRound', got '{}'"
                        .format(instance.portal_type))

    # renameAfterCreation(instance)
    num_art = len(instance.ar_templates)
    destination_url = instance.aq_parent.absolute_url() + \
        "/portal_factory/" + \
        "AnalysisRequest/Request new analyses/ar_add?samplinground=" + \
        instance.UID() + "&ar_count=" + str(num_art)
    request = getattr(instance, 'REQUEST', None)
    request.response.redirect(destination_url)
