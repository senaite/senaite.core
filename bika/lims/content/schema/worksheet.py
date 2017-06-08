# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from sys import maxsize

from Products.ATExtensions.ateapi import RecordsField
from Products.Archetypes.Field import ReferenceField, StringField, TextField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import TextAreaWidget
from Products.Archetypes.references import HoldingReference
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets import SelectionWidget
from bika.lims.config import WORKSHEET_LAYOUT_OPTIONS
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema

WorksheetTemplate = UIDReferenceField(
    'WorksheetTemplate',
    storage=Storage(),
    allowed_types=('WorksheetTemplate',)
)
Layout = RecordsField(
    'Layout',
    storage=Storage(),
    required=1,
    subfields=('position', 'type', 'container_uid', 'analysis_uid'),
    subfield_types={'position': 'int'}
)
# all layout info lives in Layout; Analyses is used for back references.
Analyses = ReferenceField(
    'Analyses',
    storage=Storage(),
    required=1,
    multiValued=1,
    allowed_types=(
        'Analysis', 'DuplicateAnalysis', 'ReferenceAnalysis',
        'RejectAnalysis'),
    relationship='WorksheetAnalysis'
)
Analyst = StringField(
    'Analyst',
    storage=Storage(),
    searchable=True
)
Method = ReferenceField(
    'Method',
    storage=Storage(),
    required=0,
    vocabulary_display_path_bound=maxsize,
    vocabulary='_getMethodsVoc',
    allowed_types=('Method',),
    relationship='WorksheetMethod',
    referenceClass=HoldingReference,
    widget=SelectionWidget(
        format='select',
        label=_("Method"),
        visible=False
    )
)
# TODO Remove. Instruments must be assigned directly to each analysis.
Instrument = ReferenceField(
    'Instrument',
    storage=Storage(),
    required=0,
    allowed_types=('Instrument',),
    vocabulary='_getInstrumentsVoc',
    relationship='WorksheetInstrument',
    referenceClass=HoldingReference
)
Remarks = TextField(
    'Remarks',
    storage=Storage(),
    searchable=True,
    default_content_type='text/plain',
    allowed_content_types=('text/plain',),
    default_output_type="text/plain",
    widget=TextAreaWidget(
        macro="bika_widgets/remarks",
        label=_("Remarks"),
        append_only=True
    )
)
ResultsLayout = StringField(
    'ResultsLayout',
    storage=Storage(),
    default='1',
    vocabulary=WORKSHEET_LAYOUT_OPTIONS
)

schema = BikaSchema.copy() + Schema((
    WorksheetTemplate,
    Layout,
    Analyses,
    Analyst,
    Method,
    Instrument,
    Remarks,
    ResultsLayout
))

schema['id'].required = 0
schema['id'].widget.visible = False
schema['title'].required = 0
schema['title'].widget.visible = {'edit': 'hidden', 'view': 'invisible'}
