# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from bika.lims.controlpanel.bika_srtemplates import SamplingRoundTemplatesView


class ClientSamplingRoundTemplatesView(SamplingRoundTemplatesView):
    """
    Displays the client-specific Sampling Round Templates.
    """

    def __init__(self, context, request):
        super(ClientSamplingRoundTemplatesView, self).__init__(context, request)
