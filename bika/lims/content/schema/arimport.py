# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from sys import maxint

from Products.Archetypes.Field import ReferenceField, StringField, LinesField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import ComputedWidget, StringWidget, \
    ReferenceWidget, LinesWidget
from Products.Archetypes.references import HoldingReference
from Products.DataGridField import CheckboxColumn
from Products.DataGridField import Column
from Products.DataGridField import DataGridField
from Products.DataGridField import DataGridWidget
from Products.DataGridField import DateColumn
from Products.DataGridField import LinesColumn
from Products.DataGridField import SelectColumn
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import ReferenceWidget as bReferenceWidget
from bika.lims.content.schema.bikaschema import BikaSchema
from plone.app.blob.field import FileField as BlobFileField
from zope.i18nmessageid import MessageFactory
from bika.lims.content.schema import Storage

_p = MessageFactory(u"plone")

OriginalFile = BlobFileField(
    'OriginalFile',
    storage=Storage,
    widget=ComputedWidget(
        visible=False
    ),
)

Filename = StringField(
    'Filename',
    storage=Storage,
    widget=StringWidget(
        label=_('Original Filename'),
        visible=True
    ),
)

NrSamples = StringField(
    'NrSamples',
    storage=Storage,
    widget=StringWidget(
        label=_('Number of samples'),
        visible=True
    ),
)

ClientName = StringField(
    'ClientName',
    storage=Storage,
    searchable=True,
    widget=StringWidget(
        label=_("Client Name"),
    ),
)

ClientID = StringField(
    'ClientID',
    storage=Storage,
    searchable=True,
    widget=StringWidget(
        label=_('Client ID'),
    ),
)

ClientOrderNumber = StringField(
    'ClientOrderNumber',
    storage=Storage,
    searchable=True,
    widget=StringWidget(
        label=_('Client Order Number'),
    ),
)

ClientReference = StringField(
    'ClientReference',
    storage=Storage,
    searchable=True,
    widget=StringWidget(
        label=_('Client Reference'),
    ),
)

Contact = ReferenceField(
    'Contact',
    storage=Storage,
    allowed_types=('Contact',),
    relationship='ARImportContact',
    default_method='getContactUIDForUser',
    referenceClass=HoldingReference,
    vocabulary_display_path_bound=maxint,
    widget=ReferenceWidget(
        label=_('Primary Contact'),
        size=20,
        visible=True,
        base_query={'inactive_state': 'active'},
        showOn=True,
        popup_width='300px',
        colModel=[{'columnName': 'UID', 'hidden': True},
                  {'columnName': 'Fullname', 'width': '100',
                   'label': _('Name')}],
    ),
)

Batch = ReferenceField(
    'Batch',
    storage=Storage,
    allowed_types=('Batch',),
    relationship='ARImportBatch',
    widget=bReferenceWidget(
        label=_('Batch'),
        visible=True,
        catalog_name='bika_catalog',
        base_query={'review_state': 'open', 'cancellation_state': 'active'},
        showOn=True,
    ),
)

CCContacts = DataGridField(
    'CCContacts',
    storage=Storage,
    allow_insert=False,
    allow_delete=False,
    allow_reorder=False,
    allow_empty_rows=False,
    columns=('CCNamesReport',
             'CCEmailsReport',
             'CCNamesInvoice',
             'CCEmailsInvoice'),
    default=[{'CCNamesReport': [],
              'CCEmailsReport': [],
              'CCNamesInvoice': [],
              'CCEmailsInvoice': []
              }],
    widget=DataGridWidget(
        columns={
            'CCNamesReport': LinesColumn('Report CC Contacts'),
            'CCEmailsReport': LinesColumn('Report CC Emails'),
            'CCNamesInvoice': LinesColumn('Invoice CC Contacts'),
            'CCEmailsInvoice': LinesColumn('Invoice CC Emails')
        }
    ),
)

SampleData = DataGridField(
    'SampleData',
    storage=Storage,
    allow_insert=True,
    allow_delete=True,
    allow_reorder=False,
    allow_empty_rows=False,
    allow_oddeven=True,
    columns=('ClientSampleID',
             'SamplingDate',
             'DateSampled',
             'SamplePoint',
             'SampleMatrix',
             'SampleType',  # not a schema field!
             'ContainerType',  # not a schema field!
             'ReportDryMatter',
             'Analyses',  # not a schema field!
             'Profiles'  # not a schema field!
             ),
    widget=DataGridWidget(
        label=_('Samples'),
        columns={
            'ClientSampleID': Column('Sample ID'),
            'SamplingDate': DateColumn('Sampling Date'),
            'DateSampled': DateColumn('Date Sampled'),
            'SamplePoint': SelectColumn(
                'Sample Point', vocabulary='Vocabulary_SamplePoint'),
            'SampleMatrix': SelectColumn(
                'Sample Matrix', vocabulary='Vocabulary_SampleMatrix'),
            'SampleType': SelectColumn(
                'Sample Type', vocabulary='Vocabulary_SampleType'),
            'ContainerType': SelectColumn(
                'Container', vocabulary='Vocabulary_ContainerType'),
            'ReportDryMatter': CheckboxColumn('Dry'),
            'Analyses': LinesColumn('Analyses'),
            'Profiles': LinesColumn('Profiles'),
        }
    ),
)

Errors = LinesField(
    'Errors',
    storage=Storage,
    widget=LinesWidget(
        label=_('Errors'),
        rows=10,
    ),
)

schema = BikaSchema.copy() + Schema((
    OriginalFile,
    Filename,
    NrSamples,
    ClientName,
    ClientID,
    ClientOrderNumber,
    ClientReference,
    Contact,
    CCContacts,
    Batch,
    SampleData,
    Errors,
))

schema['title'].validators = ()
# Update the validation layer after change the validator in runtime
schema['title']._validationLayer()
