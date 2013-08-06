from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore.permissions import View, ModifyPortalContent
from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME, ManageSuppliers
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.content.organisation import Organisation
from bika.lims.interfaces import ISupplier
from zope.interface import implements

schema = Organisation.schema.copy() + ManagedSchema((
    TextField('Remarks',
        searchable = True,
        default_content_type = 'text/plain',
        allowed_content_types= ('text/plain', ),
        default_output_type = "text/html",
        widget = TextAreaWidget(
            macro = "bika_widgets/remarks",
            label = _('Remarks'),
            append_only = True,
        ),
    ),
))
schema['AccountNumber'].write_permission = ManageSuppliers

class Supplier(Organisation):
    implements(ISupplier)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(Supplier, PROJECTNAME)
