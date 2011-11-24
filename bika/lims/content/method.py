from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import ModifyPortalContent, View
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.ATExtensions.ateapi import RecordsField as RecordsField
from bika.lims.browser.widgets import RecordsWidget
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
import sys
from bika.lims import bikaMessageFactory as _

schema = BikaSchema.copy() + Schema((
    TextField('Instructions',
        default_content_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        widget = TextAreaWidget(
            label = _("Instructions"),
            description = _("Technical description and instructions intended for analysts"),
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    FileField('MethodDocument',  # XXX Multiple Method documents please
        widget = FileWidget(
            label = _("Method document"),
            description = _("Load documents describing the method here"),
            i18n_domain = I18N_DOMAIN,
        )
    ),
))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True
schema['description'].widget.label = _("Description")
schema['description'].widget.description = _("Describes the method in layman terms. This information is made available to lab clients")


class Method(BaseFolder):
    security = ClassSecurityInfo()
    schema = schema

registerType(Method, PROJECTNAME)
