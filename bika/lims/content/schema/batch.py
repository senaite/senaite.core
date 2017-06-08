# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.Archetypes.Field import DateTimeField, LinesField, \
    ReferenceField, StringField, TextField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import MultiSelectionWidget, \
    StringWidget, TextAreaWidget
from Products.Archetypes.references import HoldingReference
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields.inheritedobjectsuifield import \
    InheritedObjectsUIField
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.browser.widgets import RecordsWidget as bikaRecordsWidget
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaFolderSchema

BatchID = StringField(
    'BatchID',
    storage=Storage(),
    searchable=True,
    required=False,
    validators=('uniquefieldvalidator',),
    widget=StringWidget(
        visible=False,
        label=_("Batch ID")
    ),
)

Client = ReferenceField(
    'Client',
    storage=Storage(),
    required=0,
    allowed_types=('Client',),
    relationship='BatchClient',
    widget=ReferenceWidget(
        label=_("Client"),
        size=30,
        visible=True,
        base_query={'inactive_state': 'active'},
        showOn=True,
        colModel=[{'columnName': 'UID', 'hidden': True},
                  {'columnName': 'Title', 'width': '60',
                   'label': _('Title')},
                  {'columnName': 'ClientID', 'width': '20',
                   'label': _('Client ID')}
                  ]
    ),
)

ClientBatchID = StringField(
    'ClientBatchID',
    storage=Storage(),
    searchable=True,
    required=0,
    widget=StringWidget(
        label=_("Client Batch ID")
    ),
)

BatchDate = DateTimeField(
    'BatchDate',
    storage=Storage(),
    required=False,
    widget=DateTimeWidget(
        label=_('Date')
    ),
)

BatchLabels = LinesField(
    'BatchLabels',
    storage=Storage(),
    vocabulary="BatchLabelVocabulary",
    accessor="getLabelNames",
    widget=MultiSelectionWidget(
        label=_("Batch Labels"),
        format="checkbox"
    ),
)

Remarks = TextField(
    'Remarks',
    storage=Storage(),
    searchable=True,
    default_content_type='text/x-web-intelligent',
    allowable_content_types=('text/plain',),
    default_output_type="text/plain",
    widget=TextAreaWidget(
        macro="bika_widgets/remarks",
        label=_('Remarks'),
        append_only=True
    ),
)

InheritedObjects = ReferenceField(
    'InheritedObjects',
    storage=Storage(),
    required=0,
    multiValued=True,
    allowed_types=('AnalysisRequest',),
    # batches are expanded on save
    referenceClass=HoldingReference,
    relationship='BatchInheritedObjects',
    widget=ReferenceWidget(
        visible=False
    ),
)

InheritedObjectsUI = InheritedObjectsUIField(
    'InheritedObjectsUI',
    storage=Storage(),
    required=False,
    type='InheritedObjects',
    subfields=('Title', 'ObjectID', 'Description'),
    subfield_sizes={'Title': 25, 'ObjectID': 25, 'Description': 50},
    subfield_labels={'Title': _('Title'),
                     'ObjectID': _('Object ID'),
                     'Description': _('Description')
                     },
    widget=bikaRecordsWidget(
        label=_("Inherit From"),
        description=_(
            "Include all analysis requests belonging to the selected objects."),
        innerJoin="<br/>",
        combogrid_options={
            'Title': {
                'colModel': [
                    {'columnName': 'Title',
                     'width': '25',
                     'label': _('Title'),
                     'align': 'left'},
                    {'columnName': 'ObjectID',
                     'width': '25',
                     'label': _('Object ID'),
                     'align': 'left'},
                    {'columnName': 'Description',
                     'width': '50',
                     'label': _('Description'),
                     'align': 'left'},
                    {'columnName': 'UID',
                     'hidden': True},
                ],
                'url':
                    'getAnalysisContainers',
                'showOn': False,
                'width': '600px'
            },
            'ObjectID': {
                'colModel': [
                    {'columnName': 'Title',
                     'width': '25',
                     'label': _('Title'),
                     'align': 'left'},
                    {'columnName': 'ObjectID',
                     'width': '25',
                     'label': _('Object ID'),
                     'align': 'left'},
                    {'columnName': 'Description',
                     'width': '50',
                     'label': _('Description'),
                     'align': 'left'},
                    {'columnName': 'UID',
                     'hidden': True},
                ],
                'url': 'getAnalysisContainers',
                'showOn': False,
                'width': '600px'
            },
        }
    ),
)

schema = BikaFolderSchema.copy() + Schema((
    BatchID,
    Client,
    ClientBatchID,
    BatchDate,
    BatchLabels,
    Remarks,
    InheritedObjects,
    InheritedObjectsUI
))

schema['title'].required = False
schema['title'].widget.visible = True
schema['title'].widget.description = _(
    "If no Title value is entered, the Batch ID will be used.")
schema['description'].required = False
schema['description'].widget.visible = True

schema.moveField('ClientBatchID', before='description')
schema.moveField('BatchID', before='description')
schema.moveField('title', before='description')
schema.moveField('Client', after='title')
