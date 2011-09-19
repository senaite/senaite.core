from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from Products.Archetypes.public import *
from Products.CMFCore.permissions import View, ModifyPortalContent
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims import bikaMessageFactory as _

schema = BikaSchema.copy() + Schema((
    StringField('Type',
        widget = StringWidget(
            label = _("Instrument type"),
        )
    ),
    StringField('Brand',
        widget = StringWidget(
            label = _("Brand"),
            description = _("The commercial 'make' of the instrument"),
        )
    ),
    StringField('Model',
        widget = StringWidget(
            label = _("Model"),
            description = _("The instrument's model number"),
        )
    ),
    StringField('SerialNo',
        widget = StringWidget(
            label = _("Serial No"),
            description = _("The serial number that uniquely identifies the instrument"),
        )
    ),
    StringField('CalibrationCertificate',
        widget = StringWidget(
            label = _("Calibration Certificate"),
            description = _("The instrument's calibration certificate and number"),
        )
    ),
    DateTimeField('CalibrationExpiryDate',
        with_time = 0,
        with_date = 1,
        widget = DateTimeWidget(
            label = _("Calibration Expiry Date"),
            description = _("Due date for next calibration"),
        ),
    ),
))
schema['description'].widget.visible = True
schema['description'].schemata = 'default'

class Instrument(BaseContent):
    security = ClassSecurityInfo()
    schema = schema

registerType(Instrument, PROJECTNAME)
