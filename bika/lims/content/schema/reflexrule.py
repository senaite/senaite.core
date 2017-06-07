# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
import sys

from Products.Archetypes.public import ReferenceField
from Products.Archetypes.public import Schema
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.references import HoldingReference
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import ReflexRuleField
from bika.lims.content.schema.bikaschema import BikaSchema
from bika.lims.content.schema import Storage

# Methods associated to the Reflex rule
# In the first place the user has to choose from a drop-down list the
# method which the rules for the analysis service will be bind to. After
# selecting the method, the system will display another list in order to
# choose the analysis service to add the rules when using the selected
# method.
Method = ReferenceField(
    'Method',
    storage=Storage,
    required=1,
    multiValued=0,
    vocabulary_display_path_bound=sys.maxint,
    vocabulary='_getAvailableMethodsDisplayList',
    allowed_types=('Method',),
    relationship='ReflexRuleMethod',
    referenceClass=HoldingReference,
    widget=SelectionWidget(
        label=_("Methods"),
        format='select',
        description=_(
            "Select the method which the rules for the analysis "
            "service will be bound to.")
    ),
)

ReflexRules = ReflexRuleField(
    'ReflexRules',
    storage=Storage,
)

schema = BikaSchema.copy() + Schema((
    Method,
    ReflexRules
))
schema['description'].widget.visible = True
schema['description'].widget.label = _("Description")
schema['description'].widget.description = _("")
