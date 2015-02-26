"""Bika's browser views are based on this one, for a nice set of utilities.
"""
from DateTime.DateTime import DateTime, safelocaltime
from DateTime.interfaces import DateTimeError
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from Products.CMFPlone.i18nl10n import ulocalized_time as _ut
from Products.Five.browser import BrowserView
from bika.lims import logger
from zope.cachedescriptors.property import Lazy as lazy_property
from zope.i18n import translate
from time import strptime as _strptime


def strptime(context, value):
    """given a string, this function tries to return a DateTime.DateTime object
    with the date formats from i18n translations
    """
    val = ""
    for fmt in ['date_format_long', 'date_format_short']:
        fmtstr = context.translate(fmt, domain='bika', mapping={})
        fmtstr = fmtstr.replace(r"${", '%').replace('}', '')
        try:
            val = _strptime(value, fmtstr)
        except ValueError:
            continue
        try:
            val = DateTime(*list(val)[:-6])
        except DateTimeError:
            val = ""
        if val.timezoneNaive():
            # Use local timezone for tz naive strings
            # see http://dev.plone.org/plone/ticket/10141
            zone = val.localZone(safelocaltime(val.timeTime()))
            parts = val.parts()[:-1] + (zone,)
            val = DateTime(*parts)
        break
    else:
        logger.warning("DateTimeField failed to format date "
                       "string '%s' with '%s'" % (value, fmtstr))
    return val


def ulocalized_time(time, long_format=None, time_only=None, context=None,
                    request=None):
    # if time is a string, we'll try pass it through strptime with the various
    # formats defined.
    if isinstance(time, basestring):
        time = strptime(context, time)
    if time:
        # no printing times if they were not specified in inputs
        if time.second() + time.minute() + time.hour() == 0:
            long_format = False
        time_str = _ut(time, long_format, time_only, context,
                                   'bika', request)
        return time_str


class BrowserView(BrowserView):
    security = ClassSecurityInfo()

    logger = logger

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)

    security.declarePublic('ulocalized_time')

    def ulocalized_time(self, time, long_format=None, time_only=None):
        return ulocalized_time(time, long_format, time_only,
                               context=self.context, request=self.request)

    @lazy_property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    @lazy_property
    def portal_url(self):
        return self.portal.absolute_url().split("?")[0]

    @lazy_property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @lazy_property
    def reference_catalog(self):
        return getToolByName(self.context, 'reference_catalog')

    @lazy_property
    def bika_analysis_catalog(self):
        return getToolByName(self.context, 'bika_analysis_catalog')

    @lazy_property
    def bika_setup_catalog(self):
        return getToolByName(self.context, 'bika_setup_catalog')

    @lazy_property
    def bika_catalog(self):
        return getToolByName(self.context, 'bika_catalog')

    @lazy_property
    def portal_membership(self):
        return getToolByName(self.context, 'portal_membership')

    @lazy_property
    def portal_groups(self):
        return getToolByName(self.context, 'portal_groups')

    @lazy_property
    def portal_workflow(self):
        return getToolByName(self.context, 'portal_workflow')

    @lazy_property
    def checkPermission(self, perm, obj):
        return self.portal_membership.checkPermission(perm, obj)

    def user_fullname(self, userid):
        member = self.portal_membership.getMemberById(userid)
        if member is None:
            return userid
        member_fullname = member.getProperty('fullname')
        c = self.portal_catalog(portal_type='Contact', getUsername=userid)
        contact_fullname = c[0].getObject().getFullname() if c else None
        return contact_fullname or member_fullname or userid

    def user_email(self, userid):
        member = self.portal_membership.getMemberById(userid)
        if member is None:
            return userid
        member_email = member.getProperty('email')
        c = self.portal_catalog(portal_type='Contact', getUsername=userid)
        contact_email = c[0].getObject().getEmailAddress() if c else None
        return contact_email or member_email or ''

    def python_date_format(self, long_format=None, time_only=False):
        """This convert bika domain date format msgstrs to Python
        strftime format strings, by the same rules as ulocalized_time.
        XXX i18nl10n.py may change, and that is where this code is taken from.
        """
        # get msgid
        msgid = long_format and 'date_format_long' or 'date_format_short'
        if time_only:
            msgid = 'time_format'
        # get the formatstring
        formatstring = translate(msgid, domain='bika', mapping={},
                                 context=self.request)
        if formatstring is None or formatstring.startswith(
                'date_') or formatstring.startswith('time_'):
            self.logger.error("bika/%s/%s could not be translated" %
                              (self.request.get('LANGUAGE'), msgid))
            # msg catalog was not able to translate this msgids
            # use default setting
            properties = getToolByName(self.context,
                                       'portal_properties').site_properties
            if long_format:
                format = properties.localLongTimeFormat
            else:
                if time_only:
                    format = properties.localTimeOnlyFormat
                else:
                    format = properties.localTimeFormat
            return format
        return formatstring.replace(r"${", '%').replace('}', '')

    @lazy_property
    def date_format_long(self):
        fmt = self.python_date_format(long_format=1)
        if fmt == "date_format_long":
            fmt = "%Y-%m-%d %I:%M %p"
        return fmt

    @lazy_property
    def date_format_short(self):
        fmt = self.python_date_format()
        if fmt == "date_format_short":
            fmt = "%Y-%m-%d"
        return fmt

    @lazy_property
    def time_format(self):
        fmt = self.python_date_format(time_only=True)
        if fmt == "time_format":
            fmt = "%I:%M %p"
        return fmt
