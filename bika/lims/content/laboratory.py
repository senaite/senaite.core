from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.permissions import ListFolderContents, \
    ModifyPortalContent, View
from plone.app import folder
from Products.Archetypes.public import *
from bika.lims.content.organisation import Organisation
from bika.lims.config import ManageBika, I18N_DOMAIN, PROJECTNAME
from bika.lims import bikaMessageFactory as _

schema = Organisation.schema.copy() + Schema((
    IntegerField('Confidence',
        schemata = 'Accreditation',
        widget = IntegerWidget(
            label = _("Confidence Level %"),
            description = _("This value is reported at the bottom of all published results"),
        ),
    ),
    StringField('LabURL',
        schemata = 'Address',
        write_permission = ManageBika,
        widget = StringWidget(
            size = 60,
            label = _("Lab URL"),
            description = _("The Laboratory's web address"),
        ),
    ),
    BooleanField('LaboratoryAccredited',
        default = True,
        schemata = 'Accreditation',
        write_permission = ManageBika,
        widget = BooleanWidget(
            label = _("Laboratory Accredited"),
            description = _("Check this box if your laboratory is accredited"),
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
    StringField('AccreditationBodyLong',
        schemata = 'Accreditation',
        write_permission = ManageBika,
        widget = StringWidget(
            size = 60,
            label = _("Accreditation Body"),
            description = _("The name of the accreditation body corresponding to the abbreviation above, "
                            " e.g. South African National Accreditation Service for SANAS"),
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
))


IdField = schema['id']
IdField.widget.visible = {'edit':'hidden', 'view': 'invisible'}

schema['Name'].validators = ()
# Update the validation layer after change the validator in runtime
schema['Name']._validationLayer()

class Laboratory(UniqueObject, Organisation):
    security = ClassSecurityInfo()
    schema = schema

    # XXX: Temporary workaround to enable importing of exported bika
    # instance. If '__replaceable__' is not set we get BadRequest, The
    # id is invalid - it is already in use.
    __replaceable__ = 1

    security.declareProtected(View, 'getSchema')
    def getSchema(self):
        return self.schema

registerType(Laboratory, PROJECTNAME)

