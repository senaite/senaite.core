from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.config import PROJECTNAME, ManageSuppliers
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.content.organisation import Organisation
from bika.lims.interfaces import ISupplier
from Products.Archetypes.public import *
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFPlone.utils import safe_unicode
from zope.interface import implements

schema = Organisation.schema.copy() + ManagedSchema((
    TextField('Remarks',
        searchable = True,
        default_content_type = 'text/plain',
        allowed_content_types= ('text/plain', ),
        default_output_type = "text/html",
        widget = TextAreaWidget(
            macro = "bika_widgets/remarks",
            label=_("Remarks"),
            append_only = True,
        ),
    ),
    StringField('Website',
        searchable=1,
        required=0,
        widget=StringWidget(
            visible={'view': 'visible', 'edit': 'visible'},
            label=_('Website.'),
        ),
    ),
    StringField('NIB',
        searchable=1,
        schemata = 'Bank details',
        required=0,
        widget=StringWidget(
            visible={'view': 'visible', 'edit': 'visible'},
            label=_('NIB'),
        ),
        validators=('NIBvalidator'),
    ),
    StringField('IBN',
        searchable=1,
        schemata ='Bank details',
        required=0,
        widget=StringWidget(
            visible={'view': 'visible', 'edit': 'visible'},
            label=_('IBN'),
        ),
        validators=('IBANvalidator'),
    ),
    StringField('SWIFTcode',
        searchable=1,
        required=0,
        schemata ='Bank details',
        widget=StringWidget(
            visible={'view': 'visible', 'edit': 'visible'},
            label=_('SWIFT code.'),
        ),
    ),
))
schema['AccountNumber'].write_permission = ManageSuppliers

class Supplier(Organisation):
    implements(ISupplier)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    def Title(self):
        """ Return the Organisation's Name as its title """
        return safe_unicode(self.getField('Name').get(self)).encode('utf-8')

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(Supplier, PROJECTNAME)
