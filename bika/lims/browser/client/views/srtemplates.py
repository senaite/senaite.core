from bika.lims.permissions import AddSRTemplate
from bika.lims.controlpanel.bika_srtemplates import SamplingRoundTemplatesView
from Products.CMFCore.utils import getToolByName


class ClientSamplingRoundTemplatesView(SamplingRoundTemplatesView):
    """
    Displays the client-specific Sampling Round Templates.
    """

    def __init__(self, context, request):
        super(ClientSamplingRoundTemplatesView, self).__init__(context, request)
