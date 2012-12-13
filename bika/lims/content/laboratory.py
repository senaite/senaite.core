from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.permissions import ListFolderContents, \
    ModifyPortalContent, View
from plone.app import folder
from Products.Archetypes.public import *
from Products.CMFPlone.utils import safe_unicode
from bika.lims.content.organisation import Organisation
from bika.lims.config import ManageBika, PROJECTNAME
from bika.lims import PMF, bikaMessageFactory as _

schema = Organisation.schema.copy() + Schema((
    StringField('LabURL',
        schemata = 'Address',
        write_permission = ManageBika,
        widget = StringWidget(
            size = 60,
            label = _("Lab URL"),
            description = _("The Laboratory's web address"),
        ),
    ),
    IntegerField('Confidence',
        schemata = 'Accreditation',
        widget = IntegerWidget(
            label = _("Confidence Level %"),
            description = _("This value is reported at the bottom of all published results"),
        ),
    ),
    BooleanField('LaboratoryAccredited',
        default = False,
        schemata = 'Accreditation',
        write_permission = ManageBika,
        widget = BooleanWidget(
            label = _("Laboratory Accredited"),
            description = _("Check this box if your laboratory is accredited"),
        ),
    ),
    StringField('AccreditationBodyLong',
        schemata = 'Accreditation',
        write_permission = ManageBika,
        widget = StringWidget(
            size = 60,
            label = _("Accreditation Body"),
            description = _("The name of the accreditation body corresponding to the abbreviation above, "
                            "e.g. South African National Accreditation Service for SANAS"),
        ),
    ),
    StringField('AccreditationBody',
        schemata = 'Accreditation',
        write_permission = ManageBika,
        widget = StringWidget(
            label = _("Accreditation Body Abbreviation"),
            description = _("E.g. SANAS, APLAC, etc."),
        ),
    ),
    StringField('AccreditationBodyURL',
        schemata = 'Accreditation',
        write_permission = ManageBika,
        widget = StringWidget(
            label = _("Accreditation Body URL"),
            description = _("Web address for the accreditation body"),
        ),
    ),
    StringField('Accreditation',
        schemata = 'Accreditation',
        write_permission = ManageBika,
        widget = StringWidget(
            label = _("Accreditation"),
            description = _("The accreditation standard that applies, e.g. ISO 17025"),
        ),
    ),
    StringField('AccreditationReference',
        schemata = 'Accreditation',
        write_permission = ManageBika,
        widget = StringWidget(
            label = _("Accreditation Reference"),
            description = _("The reference code issued to the lab by the accreditation body"),
        ),
    ),
    ImageField('AccreditationBodyLogo',
        schemata = 'Accreditation',
        widget = ImageWidget(
            label = _("Accreditation Logo"),
            description = _("Please upload the logo you are authorised to use on your "
                            "website and results reports by your accreditation body. "
                            "Maximum size is 175 x 175 pixels.")
        ),
    ),
))

IdField = schema['id']
IdField.widget.visible = {'edit':'hidden', 'view': 'invisible'}

schema['Name'].validators = ()
# Update the validation layer after change the validator in runtime
schema['Name']._validationLayer()

class Laboratory(UniqueObject, Organisation):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    security.declareProtected(View, 'getSchema')
    def getSchema(self):
        return self.schema

    def Title(self):
        title = self.title and self.title or _("Laboratory")
        return safe_unicode(title).encode('utf-8')

registerType(Laboratory, PROJECTNAME)
