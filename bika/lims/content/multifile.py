from zope.interface import implements
from Products.Archetypes import atapi
from Products.Archetypes.public import BaseContent
from bika.lims.interfaces import IMultifile
from bika.lims.content.bikaschema import BikaSchema
from bika.lims import bikaMessageFactory as _
from bika.lims import config


schema = BikaSchema.copy() + atapi.Schema((

    atapi.StringField('DocumentID',
    required=1,
    widget = atapi.StringWidget(
        label=_("Document ID"),
        )
    ),

    atapi.ReferenceField('Instrument',
        allowed_types=('Instrument',),
        relationship='InstrumentMultifile',
        widget=atapi.StringWidget(
            visible=False,
        )
    ),

    atapi.FileField('File',
    required=1,
    widget = atapi.FileWidget(
        label=_("Document"),
        description=_("File upload "),
        )
    ),

    atapi.StringField('DocumentVersion',
    widget = atapi.StringWidget(
        label=_("Document Version"),
        )
    ),

    atapi.StringField('DocumentLocation',
    widget = atapi.StringWidget(
        label=_("Document Location"),
        description=_("Location where the document set is shelved"),
        )
    ),

    atapi.StringField('DocumentType',
    required=1,
    widget = atapi.StringWidget(
        label=_("Document Type"),
        description=_("What type of document is that? A manual, a warn..."),
        )
    ),
))

TitleField = schema['title']
TitleField.required = 0
TitleField.widget.visible = False

class Multifile(BaseContent):
    # It implements the IEthnicity interface
    implements(IMultifile)
    schema = schema

# Activating the content type in Archetypes' internal types registry
atapi.registerType(Multifile, config.PROJECTNAME)
