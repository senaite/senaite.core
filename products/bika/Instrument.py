from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View, \
    ModifyPortalContent
from Products.CMFDynamicViewFTI.browserdefault import \
    BrowserDefaultMixin
from Products.Archetypes.public import *
from DateTime import DateTime
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from Products.bika.BikaContent import BikaSchema
from Products.bika.FixedPointField import FixedPointField
from Products.bika.config import I18N_DOMAIN, PROJECTNAME
from Products.bika.fixedpoint import FixedPoint

schema = BikaSchema.copy() + Schema((
    TextField('InstrumentDescription',
        widget = TextAreaWidget(
            label = 'Instrument description',
            label_msgid = 'label_instrument_description',
            i18n_domain = I18N_DOMAIN,
        )
    ),
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
        widget = DateTimeWidget(
            label = 'Calibration Expiry Date',
            label_msgid = 'label_calibrationexpirydate',
        ),
    ),
))

class Instrument(BrowserDefaultMixin, BaseContent):
    security = ClassSecurityInfo()
    archetype_name = 'Instrument'
    schema = schema
    allowed_content_types = ()
    default_view = 'tool_base_edit'
    immediate_view = 'tool_base_edit'
    content_icon = 'instrument.png'
    global_allow = 0
    filter_content_types = 0
    use_folder_tabs = 0

    actions = (
       {'id': 'edit',
        'name': 'Edit',
        'action': 'string:${object_url}/tool_base_edit',
        'permissions': (ModifyPortalContent,),
        },
    )

    factory_type_information = {
        'title': 'Instrument'
    }

registerType(Instrument, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
