from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.permissions import ListFolderContents, \
    ModifyPortalContent, View
from Products.CMFDynamicViewFTI.browserdefault import \
    BrowserDefaultMixin
from plone.app import folder
from Products.Archetypes.public import *
from bika.lims.content.organisation import Organisation
from bika.lims.config import ManageBika, I18N_DOMAIN, PROJECTNAME

schema = Organisation.schema.copy() + Schema((
    IntegerField('Confidence',
        schemata = 'default',
        widget = IntegerWidget(
            label = 'Confidence Level %',
            label_msgid = 'label_lab_confidence_level',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    StringField('LabURL',
        schemata = 'Address',
        write_permission = ManageBika,
        widget = StringWidget(
            size = 60,
            label = "Lab URL",
            label_msgid = "label_lab_url"
        ),
    ),
    BooleanField('LaboratoryAccredited',
        default = True,
        schemata = 'Accreditation',
        write_permission = ManageBika,
        widget = BooleanWidget(
            label = "Laboratory Accredited",
            label_msgid = "label_lab_accredited"
        ),
    ),
    StringField('AccreditationBody',
        schemata = 'Accreditation',
        write_permission = ManageBika,
        widget = StringWidget(
            label = "Accreditation Body Abbreviation",
            label_msgid = "label_accreditation_body"
        ),
    ),
    StringField('AccreditationBodyLong',
        schemata = 'Accreditation',
        write_permission = ManageBika,
        widget = StringWidget(
            size = 60,
            label = "Accreditation Body",
            label_msgid = "label_accreditation_body_long"
        ),
    ),
    StringField('AccreditationBodyURL',
        schemata = 'Accreditation',
        write_permission = ManageBika,
        widget = StringWidget(
            label = "Accreditation Body URL",
            label_msgid = "label_accreditation_body_url"
        ),
    ),
    StringField('Accreditation',
        schemata = 'Accreditation',
        write_permission = ManageBika,
        widget = StringWidget(
            label = "Accreditation",
            label_msgid = "label_accreditation"
        ),
    ),
    StringField('AccreditationReference',
        schemata = 'Accreditation',
        write_permission = ManageBika,
        widget = StringWidget(
            label = "Accreditation Reference",
            label_msgid = "label_accreditation_reference"
        ),
    ),
))


IdField = schema['id']
IdField.widget.visible = {'edit':'hidden', 'view': 'invisible'}

class Laboratory(BrowserDefaultMixin, UniqueObject, Organisation):
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

