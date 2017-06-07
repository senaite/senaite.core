# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.Archetypes.Field import TextField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import TextAreaWidget
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import InterimFieldsField
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets import RecordsWidget as BikaRecordsWidget, \
    ReferenceWidget
from bika.lims.content.schema.bikaschema import BikaSchema
from bika.lims.content.schema import Storage

InterimFields = InterimFieldsField(
    'InterimFields',
    storage=Storage,
    schemata='Calculation',
    widget=BikaRecordsWidget(
        label=_("Calculation Interim Fields"),
        description=_(
            "Define interim fields such as vessel mass, dilution factors, "
            "should your calculation require them. The field title specified "
            "here will be used as column headers and field descriptors where "
            "the interim fields are displayed. If 'Apply wide' is enabled the "
            "field ill be shown in a selection box on the top of the "
            "worksheet, allowing to apply a specific value to all the "
            "corresponding fields on the sheet.")
    ),
)

DependentServices = UIDReferenceField(
    'DependentServices',
    storage=Storage,
    multiValued=1,
    allowed_types=('AnalysisService',),
    widget=ReferenceWidget(
        visible=False
    ),
)

Formula = TextField(
    'Formula',
    storage=Storage,
    schemata='Calculation',
    validators=('formulavalidator',),
    default_content_type='text/plain',
    allowable_content_types=('text/plain',),
    widget=TextAreaWidget(
        label=_("Calculation Formula"),
        description=_(
            "calculation_formula_description",
            "<p>The formula you type here will be dynamically calculated when "
            "an analysis using this calculation is displayed.</p><p>To enter "
            "a Calculation, use standard maths operators,  + - * / ( ), "
            "and all keywords available, both from other Analysis Services "
            "and the Interim Fields specified here, as variables. Enclose "
            "them in square brackets [ ].</p><p>E.g, the calculation for "
            "Total Hardness, the total of Calcium (ppm) and Magnesium (ppm) "
            "ions in water, is entered as [Ca] + [Mg], where Ca and MG are the "
            "keywords for those two Analysis Services.</p>")
    ),
)

schema = BikaSchema.copy() + Schema((
    InterimFields,
    DependentServices,
    Formula
))

schema['title'].widget.visible = True
schema['title'].schemata = 'Description'
schema['description'].widget.visible = True
schema['description'].schemata = 'Description'
