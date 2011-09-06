from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.CMFCore.permissions import View, ModifyPortalContent
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims.browser.fields import DurationField
from bika.lims.browser.widgets import DurationWidget
import sys
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('bika')

schema = BikaSchema.copy() + Schema((
    StringField('Latitude',
        schemata = _('Location'),
        widget=StringWidget(
            label='Latitude',
            label_msgid='label_Latitude',
            i18n_domain=I18N_DOMAIN,
        ),
    ),
    StringField('Longitude',
        schemata = _('Location'),
        widget=StringWidget(
            label='Longitude',
            label_msgid='label_Longitude',
            i18n_domain=I18N_DOMAIN,
        ),
    ),
    StringField('Elevation',
        schemata = _('Location'),
        widget=StringWidget(
            label='Elevation',
            label_msgid='label_Elevation',
            i18n_domain=I18N_DOMAIN,
        ),
    ),
    DurationField('SamplingFrequency',
        vocabulary_display_path_bound=sys.maxint,
        widget=DurationWidget(
            label='Sampling Frequency',
            label_msgid='label_sampling_frequency',
            i18n_domain=I18N_DOMAIN,
        ),
    ),
    BooleanField('Composite',
        default=False,
        widget=BooleanWidget(
            label="Composite",
            label_msgid="label_composite",
            i18n_domain=I18N_DOMAIN,
        ),
    ),
))
schema['description'].widget.visible = True
schema['description'].schemata = 'default'

class SamplePoint(BaseContent, HistoryAwareMixin):
    security = ClassSecurityInfo()
    schema = schema

registerType(SamplePoint, PROJECTNAME)
