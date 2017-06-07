# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from sys import maxint

from Products.ATExtensions.field.records import RecordsField
from Products.Archetypes.Field import ComputedField, ReferenceField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import ComputedWidget
from Products.Archetypes.references import HoldingReference
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import ReferenceWidget, SelectionWidget, \
    ServicesWidget
from bika.lims.browser.widgets import WorksheetTemplateLayoutWidget
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema

Layout = RecordsField(
    'Layout',
    storage=Storage,
    schemata='Layout',
    required=1,
    type='templateposition',
    subfields=('pos', 'type', 'blank_ref', 'control_ref', 'dup'),
    required_subfields=('pos', 'type'),
    subfield_labels={'pos': _('Position'),
                     'type': _('Analysis Type'),
                     'blank_ref': _('Reference'),
                     'control_ref': _('Reference'),
                     'dup': _('Duplicate Of')},
    widget=WorksheetTemplateLayoutWidget(
        label=_("Worksheet Layout"),
        description=_(
            "Specify the size of the Worksheet, e.g. corresponding to a "
            "specific instrument's tray size. Then select an Analysis 'type' "
            "per Worksheet position. Where QC samples are selected, "
            "also select which Reference Sample should be used. If a "
            "duplicate analysis is selected, indicate which sample position "
            "it should be a duplicate of")
    )
)

Service = ReferenceField(
    'Service',
    storage=Storage,
    schemata='Analyses',
    required=0,
    multiValued=1,
    allowed_types=('AnalysisService',),
    relationship='WorksheetTemplateAnalysisService',
    referenceClass=HoldingReference,
    widget=ServicesWidget(
        label=_("Analysis Service"),
        description=_(
            "Select which Analyses should be included on the Worksheet")
    )
)

RestrictToMethod = ReferenceField(
    'RestrictToMethod',
    storage=Storage,
    schemata="Description",
    required=0,
    vocabulary_display_path_bound=maxint,
    vocabulary='_getMethodsVoc',
    allowed_types=('Method',),
    relationship='WorksheetTemplateMethod',
    referenceClass=HoldingReference,
    widget=SelectionWidget(
        format='select',
        label=_("Method"),
        description=_(
            "Restrict the available analysis services and instrumentsto those "
            "with the selected method. In order to apply this change to the "
            "services list, you should save the change first.")
    )
)

Instrument = ReferenceField(
    'Instrument',
    storage=Storage,
    schemata="Description",
    required=0,
    vocabulary_display_path_bound=maxint,
    vocabulary='getInstruments',
    allowed_types=('Instrument',),
    relationship='WorksheetTemplateInstrument',
    referenceClass=HoldingReference,
    widget=ReferenceWidget(
        checkbox_bound=0,
        label=_("Instrument"),
        description=_("Select the preferred instrument")
    )
)

InstrumentTitle = ComputedField(
    'InstrumentTitle',
    storage=Storage,
    expression="context.getInstrument().Title() "
               "if context.getInstrument() else ''",
    widget=ComputedWidget(
        visible=False
    )
)

schema = BikaSchema.copy() + Schema((
    Layout,
    Service,
    RestrictToMethod,
    Instrument,
    InstrumentTitle
))

schema['title'].schemata = 'Description'
schema['title'].widget.visible = True

schema['description'].schemata = 'Description'
schema['description'].widget.visible = True
