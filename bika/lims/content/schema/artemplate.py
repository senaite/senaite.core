# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from sys import maxint

from Products.ATExtensions.field.records import RecordsField
from Products.Archetypes.Field import BooleanField, ComputedField, \
    ReferenceField, TextField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import BooleanWidget, ComputedWidget, \
    TextAreaWidget
from Products.Archetypes.references import HoldingReference
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import ARTemplateAnalysesWidget
from bika.lims.browser.widgets import ARTemplatePartitionsWidget
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema

# SamplePoint and SampleType references are managed with
# accessors and mutators below to get/set a string value
# (the Title of the object), but still store a normal Reference.
# Form autocomplete widgets can then work with the Titles.
SamplePoint = ReferenceField(
    'SamplePoint',
    storage=Storage(),
    vocabulary_display_path_bound=maxint,
    allowed_types=('SamplePoint',),
    relationship='ARTemplateSamplePoint',
    referenceClass=HoldingReference,
    accessor='getSamplePoint',
    edit_accessor='getSamplePoint',
    mutator='setSamplePoint',
    widget=ReferenceWidget(
        label=_('Sample Point'),
        description=_('Location where sample was taken'),
        visible={'edit': 'visible', 'view': 'visible',
                 'add': 'visible',
                 'secondary': 'invisible'},
        catalog_name='bika_setup_catalog',
        base_query={'inactive_state': 'active'},
        showOn=True
    ),
)

ComputedField(
    'SamplePointUID',
    expression="context.Schema()['SamplePoint'].get(context).UID() "
               "if context.Schema()['SamplePoint'].get(context) else ''",
    widget=ComputedWidget(
        visible=False
    ),
)

SampleType = ReferenceField(
    'SampleType',
    storage=Storage(),
    vocabulary_display_path_bound=maxint,
    allowed_types=('SampleType',),
    relationship='ARTemplateSampleType',
    referenceClass=HoldingReference,
    accessor='getSampleType',
    edit_accessor='getSampleType',
    mutator='setSampleType',
    widget=ReferenceWidget(
        label=_('Sample Type'),
        description=_('Create a new sample of this type'),
        visible={'edit': 'visible', 'view': 'visible',
                 'add': 'visible',
                 'secondary': 'invisible'},
        catalog_name='bika_setup_catalog',
        base_query={'inactive_state': 'active'},
        showOn=True
    ),
)

ComputedField(
    'SampleTypeUID',
    expression="context.Schema()['SampleType'].get(context).UID() "
               "if context.Schema()['SampleType'].get(context) else ''",
    widget=ComputedWidget(
        visible=False
    ),
)

Composite = BooleanField(
    'Composite',
    storage=Storage(),
    default=False,
    widget=BooleanWidget(
        label=_('Composite'),
        description=_("It's a composite sample")
    ),
)

ReportDryMatter = BooleanField(
    'ReportDryMatter',
    storage=Storage(),
    default=False,
    widget=BooleanWidget(
        label=_('Report as Dry Matter'),
        description=_('These results can be reported as dry matter')
    ),
)

Remarks = TextField(
    'Remarks',
    storage=Storage(),
    searchable=True,
    default_content_type='text/plain',
    allowed_content_types=('text/plain',),
    default_output_type='text/plain',
    widget=TextAreaWidget(
        macro='bika_widgets/remarks',
        label=_('Remarks'),
        append_only=True
    ),
)

Partitions = RecordsField(
    'Partitions',
    storage=Storage(),
    schemata='Sample Partitions',
    required=0,
    type='artemplate_parts',
    subfields=(
        'part_id',
        'Container',
        'Preservation',
        'container_uid',
        'preservation_uid'),
    subfield_labels={
        'part_id': _('Partition'),
        'Container': _('Container'),
        'Preservation': _('Preservation')},
    subfield_sizes={
        'part_id': 15,
        'Container': 35,
        'Preservation': 35},
    subfield_hidden={
        'preservation_uid': True,
        'container_uid': True},
    default=[{
        'part_id': 'part-1',
        'Container': '',
        'Preservation': '',
        'container_uid': '',
        'preservation_uid': ''}],
    widget=ARTemplatePartitionsWidget(
        label=_('Sample Partitions'),
        description=_(
            "Configure the sample partitions and preservations for this "
            "template. Assign analyses to the different partitions on the "
            "template's Analyses tab"),
        combogrid_options={
            'Container': {
                'colModel': [
                    {'columnName': 'container_uid',
                     'hidden': True},
                    {'columnName': 'Container',
                     'width': '30',
                     'label': _('Container')},
                    {'columnName': 'Description',
                     'width': '70',
                     'label': _('Description')}],
                'url': 'getcontainers',
                'showOn': True,
                'width': '550px'
            },
            'Preservation': {
                'colModel': [
                    {'columnName': 'preservation_uid',
                     'hidden': True},
                    {'columnName': 'Preservation',
                     'width': '30',
                     'label': _('Preservation')},
                    {'columnName': 'Description',
                     'width': '70',
                     'label': _('Description')}],
                'url': 'getpreservations',
                'showOn': True,
                'width': '550px'
            },
        }
    ),
)

AnalysisProfile = ReferenceField(
    'AnalysisProfile',
    storage=Storage(),
    schemata='Analyses',
    required=0,
    multiValued=0,
    allowed_types=('AnalysisProfile',),
    relationship='ARTemplateAnalysisProfile',
    widget=ReferenceWidget(
        label=_('Analysis Profile'),
        description=_('The Analysis Profile selection for this template'),
        visible={'edit': 'visible', 'view': 'visible',
                 'add': 'visible',
                 'secondary': 'invisible'},
        catalog_name='bika_setup_catalog',
        base_query={'inactive_state': 'active'},
        showOn=True
    ),
)

Analyses = RecordsField(
    'Analyses',
    storage=Storage(),
    schemata='Analyses',
    required=0,
    type='analyses',
    subfields=('service_uid', 'partition'),
    subfield_labels={'service_uid': _('Title'), 'partition': _('Partition')},
    default=[],
    widget=ARTemplateAnalysesWidget(
        label=_('Analyses'),
        description=_('Select analyses to include in this template')
    ),
)

# Custom settings for the assigned analysis services
# https://jira.bikalabs.com/browse/LIMS-1324
# Fields:
#   - uid: Analysis Service UID
#   - hidden: True/False. Hide/Display in results reports
AnalysisServicesSettings = RecordsField(
    'AnalysisServicesSettings',
    storage=Storage(),
    required=0,
    subfields=('uid', 'hidden',),
    widget=ComputedWidget(visible=False)
)

schema = BikaSchema.copy() + Schema((
    SamplePoint,
    SampleType,
    Composite,
    ReportDryMatter,
    Remarks,
    Partitions,
    AnalysisProfile,
    Analyses,
    AnalysisServicesSettings
))

schema['description'].widget.visible = True
schema['title'].widget.visible = True
schema['title'].validators = ('uniquefieldvalidator',)
# Update the validation layer after change the validator in runtime
schema['title']._validationLayer()
