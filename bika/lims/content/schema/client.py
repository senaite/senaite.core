# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

"""Client - the main organisational entity in bika.
"""
import sys

from Products.Archetypes import atapi
from bika.lims import bikaMessageFactory as _
from bika.lims.config import DECIMAL_MARKS, DEFAULT_AR_SPECS, \
    EMAIL_SUBJECT_OPTIONS
from bika.lims.content.organisation import Organisation
from bika.lims.content.schema import Storage
from bika.lims.permissions import ManageClients

ClientID = atapi.StringField(
    'ClientID',
    storage=Storage,
    required=1,
    searchable=True,
    validators=('uniquefieldvalidator', 'standard_id_validator'),
    widget=atapi.StringWidget(
        label=_("Client ID")
    ),
)

BulkDiscount = atapi.BooleanField(
    'BulkDiscount',
    storage=Storage,
    default=False,
    write_permission=ManageClients,
    widget=atapi.BooleanWidget(
        label=_("Bulk discount applies")
    ),
)

MemberDiscountApplies = atapi.BooleanField(
    'MemberDiscountApplies',
    storage=Storage,
    default=False,
    write_permission=ManageClients,
    widget=atapi.BooleanWidget(
        label=_("Member discount applies")
    ),
)

CCEmails = atapi.StringField(
    'CCEmails',
    storage=Storage,
    schemata='Preferences',
    mode="rw",
    widget=atapi.StringWidget(
        label=_("CC Emails"),
        description=_("Default Emails to CC all published ARs for this client"),
        visible={
            'edit': 'visible',
            'view': 'visible',
        }
    ),
)

EmailSubject = atapi.LinesField(
    'EmailSubject',
    storage=Storage,
    schemata='Preferences',
    default=['ar', ],
    vocabulary=EMAIL_SUBJECT_OPTIONS,
    widget=atapi.MultiSelectionWidget(
        description=_("Items to be included in email subject lines"),
        label=_("Email subject line")
    ),
)

DefaultCategories = atapi.ReferenceField(
    'DefaultCategories',
    storage=Storage,
    schemata='Preferences',
    required=0,
    multiValued=1,
    vocabulary='getAnalysisCategories',
    vocabulary_display_path_bound=sys.maxint,
    allowed_types=('AnalysisCategory',),
    relationship='ClientDefaultCategories',
    widget=atapi.ReferenceWidget(
        checkbox_bound=0,
        label=_("Default categories"),
        description=_("Always expand the selected categories in client views")
    ),
)

RestrictedCategories = atapi.ReferenceField(
    'RestrictedCategories',
    storage=Storage,
    schemata='Preferences',
    required=0,
    multiValued=1,
    vocabulary='getAnalysisCategories',
    validators=('restrictedcategoriesvalidator',),
    vocabulary_display_path_bound=sys.maxint,
    allowed_types=('AnalysisCategory',),
    relationship='ClientRestrictedCategories',
    widget=atapi.ReferenceWidget(
        checkbox_bound=0,
        label=_("Restrict categories"),
        description=_("Show only selected categories in client views")
    ),
)

DefaultARSpecs = atapi.StringField(
    'DefaultARSpecs',
    storage=Storage,
    schemata="Preferences",
    default='ar_specs',
    vocabulary=DEFAULT_AR_SPECS,
    widget=atapi.SelectionWidget(
        label=_("Default AR Specifications"),
        description=_("DefaultARSpecs_description"),
        format='select',
    ),
)

DefaultDecimalMark = atapi.BooleanField(
    'DefaultDecimalMark',
    storage=Storage,
    schemata="Preferences",
    default=True,
    widget=atapi.BooleanWidget(
        label=_("Default decimal mark"),
        description=_("The decimal mark selected in Bika Setup will be used."),
    ),
)

DecimalMark = atapi.StringField(
    'DecimalMark',
    storage=Storage,
    schemata="Preferences",
    vocabulary=DECIMAL_MARKS,
    default=".",
    widget=atapi.SelectionWidget(
        label=_("Custom decimal mark"),
        description=_("Decimal mark to use in the reports from this Client."),
        format='select',
    ),
)

schema = Organisation.schema.copy() + atapi.Schema((
    ClientID,
    BulkDiscount,
    MemberDiscountApplies,
    CCEmails,
    EmailSubject,
    DefaultCategories,
    RestrictedCategories,
    DefaultARSpecs,
    DefaultDecimalMark,
    DecimalMark
))

schema['AccountNumber'].write_permission = ManageClients
schema['title'].widget.visible = False
schema['description'].widget.visible = False
schema['EmailAddress'].schemata = 'default'

schema.moveField('ClientID', after='Name')
