# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets import AnalysisSpecificationWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IAnalysisSpec
from Products.Archetypes import atapi
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import (BaseFolder, ComputedField,
                                        ComputedWidget, ReferenceWidget,
                                        Schema)
from Products.Archetypes.utils import DisplayList
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATExtensions.field.records import RecordsField
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from zope.i18n import translate
from zope.interface import implements


schema = Schema((

    UIDReferenceField(
        'SampleType',
        vocabulary="getSampleTypes",
        allowed_types=('SampleType',),
        widget=ReferenceWidget(
            checkbox_bound=0,
            label=_("Sample Type"),
        ),
    ),

    ComputedField(
        'SampleTypeTitle',
        expression="context.getSampleType().Title() if context.getSampleType() else ''",
        widget=ComputedWidget(
            visible=False,
        ),
    ),

    ComputedField(
        'SampleTypeUID',
        expression="context.getSampleType().UID() if context.getSampleType() else ''",
        widget=ComputedWidget(
            visible=False,
        ),
    ),
)) + BikaSchema.copy() + Schema((

    RecordsField(
        'ResultsRange',
        # schemata = 'Specifications',
        required=1,
        type='resultsrange',
        subfields=(
            'keyword',
            'min',
            'max',
            'warn_min',
            'warn_max',
            'hidemin',
            'hidemax',
            'rangecomment'
        ),
        required_subfields=('keyword','min','max'),
        subfield_validators={
            'min': 'analysisspecs_validator',
            'max': 'analysisspecs_validator',
        },
        subfield_labels={
            'keyword': _('Analysis Service'),
            'min': _('Min'),
            'max': _('Max'),
            'warn_min': _('Min warn'),
            'warn_max': _('Max warn'),
            'hidemin': _('< Min'),
            'hidemax': _('> Max'),
            'rangecomment': _('Range Comment'),
        },
        widget=AnalysisSpecificationWidget(
            checkbox_bound=0,
            label=_("Specifications"),
            description=_(
                "Click on Analysis Categories (against shaded background" \
                "to see Analysis Services in each category. Enter minimum " \
                "and maximum values to indicate a valid results range. " \
                "Any result outside this range will raise an alert. " \
                "A result out of range but still within the shoulders if"
                "'Min warn' and/or 'Max warn' are taken into consideration, " \
                "will raise a less severe alert. If the result is below " \
                "'< Min' the result will be shown as '< [min]'. The same " \
                "applies for results above '> Max'"),
        ),
    ),

    ComputedField(
        'ClientUID',
        expression="context.aq_parent.UID()",
        widget=ComputedWidget(
            visible=False,
        ),
    ),
))

schema['description'].widget.visible = True
schema['title'].required = True


class AnalysisSpec(BaseFolder, HistoryAwareMixin):
    """Analysis Specification
    """
    implements(IAnalysisSpec)
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the title if possible, else return the Sample type.
        Fall back on the instance's ID if there's no sample type or title.
        """
        if self.title:
            title = self.title
        else:
            sampletype = self.getSampleType()
            if sampletype:
                title = sampletype.Title()
            else:
                title = self.id
        return safe_unicode(title).encode('utf-8')

    def contextual_title(self):
        parent = self.aq_parent
        if parent == self.bika_setup.bika_analysisspecs:
            return self.title + " (" + translate(_("Lab")) + ")"
        else:
            return self.title + " (" + translate(_("Client")) + ")"

    security.declarePublic('getResultsRangeDict')

    def getResultsRangeDict(self):
        """Return a dictionary with the specification fields for each
           service. The keys of the dictionary are the keywords of each
           analysis service. Each service contains a dictionary in which
           each key is the name of the spec field:
           specs['keyword'] = {'min': value,
                               'max': value,
                               'error': value,
                               ... }
        """
        specs = {}
        subfields = self.Schema()['ResultsRange'].subfields
        for spec in self.getResultsRange():
            keyword = spec['keyword']
            specs[keyword] = {}
            for key in subfields:
                if key not in ['uid', 'keyword']:
                    specs[keyword][key] = spec.get(key, '')
        return specs

    security.declarePublic('getRemainingSampleTypes')

    def getSampleTypes(self):
        """Return all sampletypes
        """
        sampletypes = []
        bsc = getToolByName(self, 'bika_setup_catalog')
        for st in bsc(portal_type='SampleType', sort_on='sortable_title'):
            sampletypes.append((st.UID, st.Title))

        return DisplayList(sampletypes)

    def getClientUID(self):
        return self.aq_parent.UID()


atapi.registerType(AnalysisSpec, PROJECTNAME)
