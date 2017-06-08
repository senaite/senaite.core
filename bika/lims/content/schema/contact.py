# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.Archetypes.Field import BooleanField, LinesField, ReferenceField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import BooleanWidget, MultiSelectionWidget
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.content.person import Person
from bika.lims.content.schema import Storage

ACTIVE_STATES = ["active"]

PublicationPreference = LinesField(
    'PublicationPreference',
    storage=Storage(),
    vocabulary_factory='bika.lims.vocabularies.CustomPubPrefVocabularyFactory',
    schemata='Publication preference',
    widget=MultiSelectionWidget(
        label=_("Publication preference"),
    ),
)

AttachmentsPermitted = BooleanField(
    'AttachmentsPermitted',
    storage=Storage(),
    default=False,
    schemata='Publication preference',
    widget=BooleanWidget(
        label=_("Results attachments permitted"),
        description=_(
            "File attachments to results, e.g. microscope photos, will be "
            "included in emails to recipients if this option is enabled")
    ),
)

CCContact = ReferenceField(
    'CCContact',
    storage=Storage(),
    schemata='Publication preference',
    vocabulary='getContacts',
    multiValued=1,
    allowed_types=('Contact',),
    relationship='ContactContact',
    widget=ReferenceWidget(
        checkbox_bound=0,
        label=_("Contacts to CC"),
    ),
)

schema = Person.schema.copy() + Schema((
    PublicationPreference,
    AttachmentsPermitted,
    CCContact
))

schema['JobTitle'].schemata = 'default'
schema['Department'].schemata = 'default'
# Don't make title required - it will be computed from the Person's Fullname
schema['title'].required = 0
schema['title'].widget.visible = False
schema.moveField('CCContact', before='AttachmentsPermitted')
