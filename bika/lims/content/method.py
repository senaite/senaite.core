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
        widget = TextAreaWidget(
            label = _("Instructions"),
            description = _("Technical description and instructions intended for analysts"),
        ),
    ),
    FileField('MethodDocument',  # XXX Multiple documents please
        widget = FileWidget(
            label = _("Method document"),
            description = _("Load documents describing the method here"),
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
