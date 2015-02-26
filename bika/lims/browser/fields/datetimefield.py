from time import strptime

from AccessControl import ClassSecurityInfo

from DateTime.DateTime import DateTime, safelocaltime
from DateTime.interfaces import DateTimeError
from Products.Archetypes.Registry import registerField
from Products.Archetypes.interfaces import IDateTimeField
from Products.Archetypes.public import *
from Products.Archetypes.public import DateTimeField as DTF
from bika.lims import logger
from zope.interface import implements


class DateTimeField(DTF):
    """A field that stores dates and times
    This is identical to the AT widget on which it's based, but it checks
    the i18n translation values for date formats.  This does not specifically
    check the date_format_short_datepicker, so this means that date_formats
    should be identical between the python strftime and the jquery version.
    """

    _properties = Field._properties.copy()
    _properties.update({
        'type': 'datetime',
        'widget': CalendarWidget,
    })

    implements(IDateTimeField)

    security = ClassSecurityInfo()

    security.declarePrivate('set')

    def set(self, instance, value, **kwargs):
        """
        Check if value is an actual date/time value. If not, attempt
        to convert it to one; otherwise, set to None. Assign all
        properties passed as kwargs to object.
        """
        val = value
        if not value:
            val = None
        elif not isinstance(value, DateTime):
            for fmt in ['date_format_long', 'date_format_short']:
                fmtstr = instance.translate(fmt, domain='bika', mapping={})
                fmtstr = fmtstr.replace(r"${", '%').replace('}', '')
                try:
                    val = strptime(value, fmtstr)
                except ValueError:
                    continue
                try:
                    val = DateTime(*list(val)[:-6])
                except DateTimeError:
                    val = None
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

        super(DateTimeField, self).set(instance, val, **kwargs)

registerField(DateTimeField,
              title='Date Time',
              description='Used for storing date/time')
