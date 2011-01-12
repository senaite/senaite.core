from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.permissions import ListFolderContents, \
    ModifyPortalContent, View
from Products.CMFDynamicViewFTI.browserdefault import \
    BrowserDefaultMixin
from Products.Archetypes.public import *
from Products.BikaMembers import Organisation
from Products.bika.config import ManageBika, I18N_DOMAIN, PROJECTNAME

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

class Laboratory(BrowserDefaultMixin, UniqueObject, Organisation.Organisation):
    security = ClassSecurityInfo()
    archetype_name = 'Laboratory'
    schema = schema
    content_icon = 'client.png'
    allowed_content_types = ('Address',)
    default_view = 'tool_base_edit'
    immediate_view = 'tool_base_edit'
    use_folder_tabs = 0
    global_allow = 0
    filter_content_types = 0
    id = 'laboratory'
    # XXX: Temporary workaround to enable importing of exported bika
    # instance. If '__replaceable__' is not set we get BadRequest, The
    # id is invalid - it is already in use.
    __replaceable__ = 1

    actions = (
       {'id': 'edit',
        'name': 'Edit',
        'action': 'string:${object_url}/tool_base_edit',
        'permissions': (ModifyPortalContent,),
        },
       # Make view action the same as edit
       {'id': 'view',
        'name': 'View',
        'action': 'string:${object_url}/tool_base_edit',
        'permissions': (ModifyPortalContent,),
        },
    )


    security.declareProtected(View, 'getSchema')
    def getSchema(self):
        return self.schema

registerType(Laboratory, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('view', 'syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
