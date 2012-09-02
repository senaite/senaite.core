"""Bika's browser views are based on this one, for a nice set of utilities.
"""

from AccessControl import ClassSecurityInfo
from Products.CMFPlone.i18nl10n import ulocalized_time
from Products.Five.browser import BrowserView

class BrowserView(BrowserView):

    security = ClassSecurityInfo()

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)

    security.declarePublic('ulocalized_time')
    def ulocalized_time(self, time, long_format=None, time_only=None):
        return ulocalized_time(time, long_format, time_only, self.context,
                               'plonelocales', self.request)
