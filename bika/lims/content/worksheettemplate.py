# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner
from Products.ATExtensions.field.records import RecordsField
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from bika.lims.browser.widgets import ServicesWidget
from bika.lims.browser.widgets import WorksheetTemplateLayoutWidget
from bika.lims.config import ANALYSIS_TYPES, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims import PMF, bikaMessageFactory as _
from Products.Archetypes.atapi import BooleanField
from Products.Archetypes.atapi import BooleanWidget
from zope.interface import implements
import sys

schema = BikaSchema.copy() + Schema((
    RecordsField('Layout',
        schemata = 'Layout',
        required = 1,
        type = 'templateposition',
        subfields = ('pos', 'type', 'blank_ref', 'control_ref', 'dup'),
        required_subfields = ('pos', 'type'),
        subfield_labels = {'pos': _('Position'),
                           'type': _('Analysis Type'),
                           'blank_ref': _('Reference'),
                           'control_ref': _('Reference'),
                           'dup': _('Duplicate Of')},
        widget = WorksheetTemplateLayoutWidget(
            label=_("Worksheet Layout"),
            description =_(
                "Specify the size of the Worksheet, e.g. corresponding to a "
                "specific instrument's tray size. Then select an Analysis 'type' "
                "per Worksheet position. Where QC samples are selected, also select "
                "which Reference Sample should be used. If a duplicate analysis is "
                "selected, indicate which sample position it should be a duplicate of"),
        )
    ),
    ReferenceField('Service',
        schemata = 'Analyses',
        required = 0,
        multiValued = 1,
        allowed_types = ('AnalysisService',),
        relationship = 'WorksheetTemplateAnalysisService',
        referenceClass = HoldingReference,
        widget = ServicesWidget(
            label=_("Analysis Service"),
            description=_("Select which Analyses should be included on the Worksheet"),
        )
    ),
    ReferenceField(
        'RestrictToMethod',
        schemata="Description",
        required=0,
        vocabulary_display_path_bound=sys.maxint,
        vocabulary='_getMethodsVoc',
        allowed_types=('Method',),
        relationship='WorksheetTemplateMethod',
        referenceClass=HoldingReference,
        widget = SelectionWidget(
            format='select',
            label=_("Method"),
            description=_(
                "Restrict the available analysis services and instruments"
                "to those with the selected method."
                " In order to apply this change to the services list, you "
                "should save the change first."),
        ),
    ),
    ReferenceField('Instrument',
        schemata = "Description",
        required = 0,
        vocabulary_display_path_bound = sys.maxint,
        vocabulary = 'getInstruments',
        allowed_types = ('Instrument',),
        relationship = 'WorksheetTemplateInstrument',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 0,
            label=_("Instrument"),
            description=_("Select the preferred instrument"),
        ),
    ),
    ComputedField('InstrumentTitle',
        expression = "context.getInstrument() and context.getInstrument().Title() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    BooleanField(
        'EnableMultipleUseOfInstrument',
        default=True,
        schemata="Description",
        widget=BooleanWidget(
            label=_("Enable Multiple Use of Instrument in Worksheets."),
            description=_("If unchecked, \
                          Lab Managers won't be able to assign the same Instrument more than one Analyses while \
                          creating a Worksheet.")
        )
    ),
))

schema['title'].schemata = 'Description'
schema['title'].widget.visible = True

schema['description'].schemata = 'Description'
schema['description'].widget.visible = True


class WorksheetTemplate(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    security.declarePublic('getAnalysisTypes')
    def getAnalysisTypes(self):
        """ return Analysis type displaylist """
        return ANALYSIS_TYPES

    def getInstruments(self):
        cfilter = {'portal_type': 'Instrument', 'inactive_state': 'active'}
        if self.getRestrictToMethod():
            cfilter['getMethodUIDs'] = {
                                    "query": self.getRestrictToMethod().UID(),
                                    "operator": "or"}
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('', 'No instrument')] + [
            (o.UID, o.Title) for o in
            bsc(cfilter)]
        o = self.getInstrument()
        if o and o.UID() not in [i[0] for i in items]:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def getMethodUID(self):
        method = self.getRestrictToMethod()
        if method:
            return method.UID()
        return ''

    def _getMethodsVoc(self):
        """
        This function returns the registered methods in the system as a
        vocabulary.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(i.UID, i.Title)
                 for i in bsc(portal_type='Method',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        items.insert(0, ('', _("Not specified")))
        return DisplayList(list(items))

registerType(WorksheetTemplate, PROJECTNAME)
