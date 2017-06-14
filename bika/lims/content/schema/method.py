# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.Archetypes.Field import BooleanField, ComputedField, LinesField, \
    StringField, TextField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import BooleanWidget, FileWidget, \
    MultiSelectionWidget, ReferenceWidget, StringWidget, TextAreaWidget
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema
from plone.app.blob.field import FileField as BlobFileField

# Method ID should be unique, specified on MethodSchemaModifier
MethodID = StringField(
    'MethodID',
    storage=Storage(),
    searchable=1,
    required=0,
    validators=('uniquefieldvalidator',),
    widget=StringWidget(
        visible={'view': 'visible', 'edit': 'visible'},
        label=_('Method ID'),
        description=_(
            'Define an identifier code for the method. It must be unique.')
    ),
)

Instructions = TextField(
    'Instructions',
    storage=Storage(),
    default_content_type='text/plain',
    allowed_content_types=('text/plain',),
    default_output_type="text/plain",
    widget=TextAreaWidget(
        label=_("Method Instructions",
                "Instructions"),
        description=_(
            "Technical description and instructions intended for analysts")
    ),
)

MethodDocument = BlobFileField(
    'MethodDocument',  # XXX Multiple Method documents please
    storage=Storage(),
    widget=FileWidget(
        label=_("Method Document"),
        description=_("Load documents describing the method here")
    ),
)

# The instruments linked to this method. Don't use this
# method, use getInstrumentUIDs() or getInstruments() instead
_Instruments = LinesField(
    '_Instruments',
    storage=Storage(),
    vocabulary='getInstrumentsDisplayList',
    widget=MultiSelectionWidget(
        modes=('edit',),
        label=_("Instruments"),
        description=_(
            "The selected instruments have support for this method. "
            "Use the Instrument edit view to assign "
            "the method to a specific instrument")
    ),
)

# All the instruments available in the system. Don't use this
# method to retrieve the instruments linked to this method, use
# getInstruments() or getInstrumentUIDs() instead.
_AvailableInstruments = LinesField(
    '_AvailableInstruments',
    storage=Storage(),
    vocabulary='_getAvailableInstrumentsDisplayList',
    widget=MultiSelectionWidget(
        modes=('edit',)
    ),
)

# If no instrument selected, always True. Otherwise, the user will
# be able to set or unset the value. The behavior for this field
# is controlled with javascript.
ManualEntryOfResults = BooleanField(
    'ManualEntryOfResults',
    storage=Storage(),
    default=False,
    widget=BooleanWidget(
        label=_("Manual entry of results"),
        description=_(
            "The results for the Analysis Services that use this method can "
            "be set manually"),
        modes=('edit',)
    ),
)

# Only shown in readonly view. Not in edit view
ManualEntryOfResultsViewField = ComputedField(
    'ManualEntryOfResultsViewField',
    expression="context.isManualEntryOfResults()",
    widget=BooleanWidget(
        label=_("Manual entry of results"),
        description=_(
            "The results for the Analysis Services that use this method can "
            "be set manually"),
        modes=('view',)
    ),
)

# Calculations associated to this method. The analyses services
# with this method assigned will use the calculation selected here.
Calculation = UIDReferenceField(
    'Calculation',
    storage=Storage(),
    vocabulary='_getCalculations',
    allowed_types=('Calculation',),
    widget=ReferenceWidget(
        checkbox_bound=0,
        label=_("Calculation"),
        description=_(
            "If required, select a calculation for the The analysis "
            "services linked to this method. Calculations can be "
            "configured under the calculations item in the LIMS set-up"),
        catalog_name='bika_setup_catalog',
        base_query={'inactive_state': 'active'}
    ),
)

Accredited = BooleanField(
    'Accredited',
    storage=Storage(),
    schemata="default",
    default=True,
    widget=BooleanWidget(
        label=_("Accredited"),
        description=_("Check if the method has been accredited"))
)

schema = BikaSchema.copy() + Schema((
    MethodID,
    Instructions,
    MethodDocument,
    _Instruments,
    _AvailableInstruments,
    ManualEntryOfResults,
    ManualEntryOfResultsViewField,
    Calculation,
    Accredited
))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True
schema['description'].widget.label = _("Description")
schema['description'].widget.description = _(
    "Describes the method in layman terms. This information is made available "
    "to lab clients")
