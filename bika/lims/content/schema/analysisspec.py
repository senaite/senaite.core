# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.ATExtensions.field.records import RecordsField
from Products.Archetypes.Field import ComputedField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import ComputedWidget
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets import AnalysisSpecificationWidget, \
    ReferenceWidget
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema

SampleType = UIDReferenceField(
    'SampleType',
    storage=Storage(),
    vocabulary="getSampleTypes",
    allowed_types=('SampleType',),
    widget=ReferenceWidget(
        checkbox_bound=0,
        label=_("Sample Type")
    ),
)

SampleTypeTitle = ComputedField(
    'SampleTypeTitle',
    expression="context.getSampleType().Title() "
               "if context.getSampleType() else ''",
    widget=ComputedWidget(
        visible=False
    ),
)
SampleTypeUID = ComputedField(
    'SampleTypeUID',
    expression="context.getSampleType().UID() "
               "if context.getSampleType() else ''",
    widget=ComputedWidget(
        visible=False
    ),
)

ResultsRange = RecordsField(
    'ResultsRange',
    storage=Storage(),
    # schemata = 'Specifications',
    required=1,
    type='resultsrange',
    subfields=(
        'keyword', 'min', 'max', 'error', 'hidemin', 'hidemax', 'rangecomment'),
    required_subfields=('keyword', 'error'),
    subfield_validators={'min': 'analysisspecs_validator',
                         'max': 'analysisspecs_validator',
                         'error': 'analysisspecs_validator', },
    subfield_labels={'keyword': _('Analysis Service'),
                     'min': _('Min'),
                     'max': _('Max'),
                     'error': _('% Error'),
                     'hidemin': _('< Min'),
                     'hidemax': _('> Max'),
                     'rangecomment': _('Range Comment')},
    widget=AnalysisSpecificationWidget(
        checkbox_bound=0,
        label=_("Specifications"),
        description=_(
            "Click on Analysis Categories (against shaded backgroundto see "
            "Analysis Services in each category. Enter minimum and maximum "
            "values to indicate a valid results range. Any result outside "
            "this range will raise an alert. The % Error field allows for an "
            "% uncertainty to be considered when evaluating results against "
            "minimum and maximum values. A result out of range but still in "
            "range if the % error is taken into consideration, will raise a "
            "less severe alert. If the result is below '< Min' the result "
            "will be shown as '< [min]'. The same applies for results above "
            "'> Max'")
    ),
)

ClientUID = ComputedField(
    'ClientUID',
    expression="context.aq_parent.UID()",
    widget=ComputedWidget(
        visible=False
    ),
)

schema = Schema((
    SampleType,
    SampleTypeTitle,
    SampleTypeUID,
)) + BikaSchema.copy() + Schema((
    ResultsRange,
    ClientUID
))

schema['description'].widget.visible = True
schema['title'].required = True
