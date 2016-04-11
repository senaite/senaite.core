from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import Schema
from Products.Archetypes.public import BaseContent
from Products.Archetypes import atapi
from zope.interface import implements
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IReflexRule

schema = BikaSchema.copy() + Schema((


))
schema['description'].widget.visible = True
schema['description'].widget.label = _("Description")


class ReflexRule(BaseContent):
    """
    When results become available, some samples may have to be added to the
    next available worksheet for reflex testing. These situations are caused by
    the indetermination of the result or by a failed test.
    """
    implements(IReflexRule)
    security = ClassSecurityInfo()
    schema = schema
    _at_rename_after_creation = True
    
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

atapi.registerType(ReflexRule, PROJECTNAME)
