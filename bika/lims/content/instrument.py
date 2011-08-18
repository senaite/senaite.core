from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from Products.Archetypes.public import *
from Products.CMFCore.permissions import View, ModifyPortalContent
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('bika')

schema = BikaSchema.copy() + Schema((
    StringField('Type',
        widget = StringWidget(
            label_msgid = 'label_type',
        )
    ),
    StringField('Brand',
        widget = StringWidget(
            label_msgid = 'label_brand',
        )
    ),
    StringField('Model',
        widget = StringWidget(
            label_msgid = 'label_model',
        )
    ),
    StringField('SerialNo',
        widget = StringWidget(
            label = 'Serial No',
            label_msgid = 'label_serialno',
        )
    ),
    StringField('CalibrationCertificate',
        widget = StringWidget(
            label = 'Calibration Certificate',
            label_msgid = 'label_calibrationcertificate',
        )
    ),
    DateTimeField('CalibrationExpiryDate',
        with_time = 0,
        with_date = 1,
        widget = DateTimeWidget(
            label = 'Calibration Expiry Date',
            label_msgid = 'label_calibrationexpirydate',
        ),
    ),
))
schema['description'].widget.visible = True
schema['description'].schemata = 'default'

class Instrument(BaseContent, HistoryAwareMixin):
    security = ClassSecurityInfo()
    schema = schema

registerType(Instrument, PROJECTNAME)
