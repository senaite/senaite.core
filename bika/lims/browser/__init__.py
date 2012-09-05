"""Bika's browser views are based on this one, for a nice set of utilities.
"""

from AccessControl import ClassSecurityInfo
from Products.CMFPlone.i18nl10n import ulocalized_time
from Products.Five.browser import BrowserView
from bika.lims import logger
from zope.i18n import translate

class BrowserView(BrowserView):

    security = ClassSecurityInfo()

    logger = logger

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)

    security.declarePublic('ulocalized_time')
    def ulocalized_time(self, time, long_format=None, time_only=None):
        return ulocalized_time(time, long_format, time_only, self.context,
                               'plonelocales', self.request)

    def python_date_format(self, long_format=None, time_only=False):
        """This convert plonelocales date format msgstrs to Python
        strftime format strings, by the same rules as ulocalized_time.
        XXX i18nl10n.py may change, and that is where this code is taken from.
        """
        # get msgid
        msgid = long_format and 'date_format_long' or 'date_format_short'
        if time_only:
            msgid = 'time_format'
        # get the formatstring
        formatstring = translate(msgid, 'plonelocales', {}, self.request)
        if formatstring is None or formatstring.startswith('date_') or formatstring.startswith('time_'):
            # msg catalog was not able to translate this msgids
            # use default setting
            properties = getToolByName(context, 'portal_properties').site_properties
            if long_format:
                format = properties.localLongTimeFormat
            else:
                if time_only:
                    format = properties.localTimeOnlyFormat
                else:
                    format = properties.localTimeFormat
            return format
        return formatstring.replace(r"${", '%').replace('}', '')
