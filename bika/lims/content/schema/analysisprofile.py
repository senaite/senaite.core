# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.ATExtensions.field import RecordsField
from Products.Archetypes.Field import BooleanField, ComputedField, \
    FixedPointField, ReferenceField, StringField, TextField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import BooleanWidget, ComputedWidget, \
    DecimalWidget, StringWidget, TextAreaWidget
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import AnalysisProfileAnalysesWidget
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema

ProfileKey = StringField(
    'ProfileKey',
    storage=Storage(),
    widget=StringWidget(
        label=_("Profile Keyword"),
        description=_(
            "The profile's keyword is used to uniquely identify it in import "
            "files. It has to be unique, and it may  not be the same as any "
            "Calculation Interim field ID."),
    ),
)

Service = ReferenceField(
    'Service',
    storage=Storage(),
    schemata='Analyses',
    required=1,
    multiValued=1,
    allowed_types=('AnalysisService',),
    relationship='AnalysisProfileAnalysisService',
    widget=AnalysisProfileAnalysesWidget(
        label=_("Profile Analyses"),
        description=_(
            "The analyses included in this profile, grouped per category"),
    ),
)

Remarks = TextField(
    'Remarks',
    storage=Storage(),
    searchable=True,
    default_content_type='text/plain',
    allowable_content_types=('text/plain',),
    default_output_type="text/plain",
    widget=TextAreaWidget(
        macro="bika_widgets/remarks",
        label=_("Remarks"),
        append_only=True,
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
    widget=ComputedWidget(visible=False),
)

CommercialID = StringField(
    'CommercialID',
    storage=Storage(),
    searchable=1,
    required=0,
    schemata='Accounting',
    widget=StringWidget(
        visible={'view': 'visible', 'edit': 'visible'},
        label=_('Commercial ID'),
        description=_("The profile's commercial ID for accounting purposes."),
    ),
)

# When it's set, the system uses the analysis profile's price to quote and
# the system's VAT is overridden by the
# the analysis profile's specific VAT
UseAnalysisProfilePrice = BooleanField(
    'UseAnalysisProfilePrice',
    storage=Storage(),
    default=False,
    schemata='Accounting',
    widget=BooleanWidget(
        label=_("Use Analysis Profile Price"),
        description=_(
            "When it's set, the system uses the analysis profile's price to "
            "quote and the system's VAT is overridden by the analysis "
            "profile's specific VAT"),
    ),
)

# The price will only be used if the checkbox "use analysis profiles' price"
# is set. This price will be used to quote the analyses instead of analysis
# service's price.
AnalysisProfilePrice = FixedPointField(
    'AnalysisProfilePrice',
    storage=Storage(),
    schemata="Accounting",
    default='0.00',
    widget=DecimalWidget(
        label=_("Price (excluding VAT)"),
        visible={'view': 'visible', 'edit': 'visible'},
    ),
)

# When the checkbox "use analysis profiles' price" is set,
# the AnalysisProfilesVAT should override the system's VAT
AnalysisProfileVAT = FixedPointField(
    'AnalysisProfileVAT',
    storage=Storage(),
    schemata="Accounting",
    default='14.00',
    widget=DecimalWidget(
        label=_("VAT %"),
        description=_(
            "Enter percentage value eg. 14.0. This percentage is applied on "
            "the Analysis Profile only, overriding the systems VAT"),
        visible={'view': 'visible', 'edit': 'visible'},
    ),
)

# This VAT amount is computed using the AnalysisProfileVAT instead of systems
#  VAT
VATAmount = ComputedField(
    'VATAmount',
    schemata="Accounting",
    expression='context.getVATAmount()',
    widget=ComputedWidget(
        label=_("VAT"),
        visible={'view': 'visible', 'edit': 'invisible'},
    ),
)

TotalPrice = ComputedField(
    'TotalPrice',
    schemata="Accounting",
    expression='context.getTotalPrice()',
    widget=ComputedWidget(
        label=_("Total price"),
        visible={'edit': 'hidden', }
    ),
)

schema = BikaSchema.copy() + Schema((
    ProfileKey,
    Service,
    Remarks,
    AnalysisServicesSettings,
    CommercialID,
    UseAnalysisProfilePrice,
    AnalysisProfilePrice,
    AnalysisProfileVAT,
    VATAmount,
    TotalPrice
))
schema['title'].widget.visible = True
schema['description'].widget.visible = True
IdField = schema['id']
