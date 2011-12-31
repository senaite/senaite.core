from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import ModifyPortalContent, View
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.ATExtensions.ateapi import RecordsField as RecordsField
from bika.lims.browser.widgets import RecordsWidget
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IGenerateUniqueId
from bika.lims.config import PROJECTNAME
import sys
from bika.lims import bikaMessageFactory as _
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    TextField('Instructions',
        default_content_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        widget = TextAreaWidget(
            label = _("Method Instructions",
                      "Instructions"),
            description = _("Method Instructions description",
                            "Technical description and instructions intended for analysts"),
        ),
    ),
    FileField('MethodDocument',  # XXX Multiple Method documents please
        widget = FileWidget(
            label = _("Method Document"),
            description = _("Method Document description",
                            "Load documents describing the method here"),
        )
    ),
))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True
schema['description'].widget.label = _("Method Description",
                                       "Description")
schema['description'].widget.description = _("Method Description description",
                                             "Describes the method in layman terms. This information is made available to lab clients")

class Method(BaseFolder):
    implements(IGenerateUniqueId)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

registerType(Method, PROJECTNAME)
