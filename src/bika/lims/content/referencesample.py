# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

"""ReferenceSample represents a reference sample used for quality control testing
"""

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore import permissions
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from bika.lims import PMF, bikaMessageFactory as _, api
from bika.lims.browser.fields.remarksfield import RemarksField
from bika.lims.idserver import renameAfterCreation
from bika.lims.utils import t
from bika.lims.browser.fields import ReferenceResultsField
from bika.lims.browser.widgets import DateTimeWidget as bika_DateTimeWidget
from bika.lims.browser.widgets import RemarksWidget
from bika.lims.browser.widgets import ReferenceResultsWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IReferenceSample, IAnalysisService, \
    IDeactivable
from bika.lims.utils import sortable_title, tmpID
from bika.lims.utils import to_unicode as _u
from bika.lims.utils import to_utf8
from zope.interface import implements
import sys, time

schema = BikaSchema.copy() + Schema((
    ReferenceField('ReferenceDefinition',
        schemata = 'Description',
        allowed_types = ('ReferenceDefinition',),
        relationship = 'ReferenceSampleReferenceDefinition',
        referenceClass = HoldingReference,
        vocabulary = "getReferenceDefinitions",
        widget = ReferenceWidget(
            checkbox_bound = 0,
            label=_("Reference Definition"),
        ),
    ),
    BooleanField('Blank',
        schemata = 'Description',
        default = False,
        widget = BooleanWidget(
            label=_("Blank"),
            description=_("Reference sample values are zero or 'blank'"),
        ),
    ),
    BooleanField('Hazardous',
        schemata = 'Description',
        default = False,
        widget = BooleanWidget(
            label=_("Hazardous"),
            description=_("Samples of this type should be treated as hazardous"),
        ),
    ),
    ReferenceField('Manufacturer',
        schemata = 'Description',
        allowed_types = ('Manufacturer',),
        relationship = 'ReferenceSampleManufacturer',
        vocabulary = "getManufacturers",
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 0,
            label=_("Manufacturer"),
        ),
    ),
    StringField('CatalogueNumber',
        schemata = 'Description',
        widget = StringWidget(
            label=_("Catalogue Number"),
        ),
    ),
    StringField('LotNumber',
        schemata = 'Description',
        widget = StringWidget(
            label=_("Lot Number"),
        ),
    ),
    TextField(
        "Remarks",
        allowable_content_types=("text/plain",),
        schemata="Description",
        widget=TextAreaWidget(
            label=_("Remarks"),
        )
    ),
    DateTimeField('DateSampled',
        schemata = 'Dates',
        widget = bika_DateTimeWidget(
            label=_("Date Sampled"),
        ),
    ),
    DateTimeField('DateReceived',
        schemata = 'Dates',
        default_method = 'current_date',
        widget = bika_DateTimeWidget(
            label=_("Date Received"),
        ),
    ),
    DateTimeField('DateOpened',
        schemata = 'Dates',
        widget = bika_DateTimeWidget(
            label=_("Date Opened"),
        ),
    ),
    DateTimeField('ExpiryDate',
        schemata = 'Dates',
        required = 1,
        widget = bika_DateTimeWidget(
            label=_("Expiry Date"),
        ),
    ),
    DateTimeField('DateExpired',
        schemata = 'Dates',
        widget = bika_DateTimeWidget(
            label=_("Date Expired"),
            visible = {'edit':'hidden'},
        ),
    ),
    DateTimeField('DateDisposed',
        schemata = 'Dates',
        widget = bika_DateTimeWidget(
            label=_("Date Disposed"),
            visible = {'edit':'hidden'},
        ),
    ),
    ReferenceResultsField('ReferenceResults',
        schemata = 'Reference Values',
        required = 1,
        subfield_validators = {
                    'result':'referencevalues_validator',},
        widget = ReferenceResultsWidget(
            label=_("Expected Values"),
        ),
    ),
    ComputedField('SupplierUID',
        expression = 'context.aq_parent.UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ReferenceDefinitionUID',
        expression = 'here.getReferenceDefinition() and here.getReferenceDefinition().UID() or None',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
))

schema['title'].schemata = 'Description'

class ReferenceSample(BaseFolder):
    implements(IReferenceSample, IDeactivable)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    security.declarePublic('current_date')
    def current_date(self):
        return DateTime()

    def getReferenceDefinitions(self):

        def make_title(o):
            # the javascript uses these strings to decide if it should
            # check the blank or hazardous checkboxes when a reference
            # definition is selected (./js/referencesample.js)
            if not o:
                return ''
            title = _u(o.Title())
            if o.getBlank():
                title += " %s" % t(_('(Blank)'))
            if o.getHazardous():
                title += " %s" % t(_('(Hazardous)'))

            return title

        bsc = getToolByName(self, 'bika_setup_catalog')
        defs = [o.getObject() for o in
                bsc(portal_type = 'ReferenceDefinition',
                    is_active = True)]
        items = [('','')] + [(o.UID(), make_title(o)) for o in defs]
        o = self.getReferenceDefinition()
        it = make_title(o)
        if o and (o.UID(), it) not in items:
            items.append((o.UID(), it))
        items.sort(lambda x,y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    def getManufacturers(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('','')] + [(o.UID, o.Title) for o in
                               bsc(portal_type='Manufacturer',
                                   is_active = True)]
        o = self.getReferenceDefinition()
        if o and o.UID() not in [i[0] for i in items]:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x,y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    security.declarePublic('getResultsRangeDict')
    def getResultsRangeDict(self):
        specs = {}
        for spec in self.getReferenceResults():
            uid = spec['uid']
            specs[uid] = {}
            specs[uid]['result'] = spec['result']
            specs[uid]['min'] = spec.get('min', '')
            specs[uid]['max'] = spec.get('max', '')
        return specs

    def getSupportedServices(self, only_uids=True):
        """Return a list with the services supported by this reference sample,
        those for which there is a valid results range assigned in reference
        results
        :param only_uids: returns a list of uids or a list of objects
        :return: list of uids or AnalysisService objects
        """
        uids = map(lambda range: range['uid'], self.getReferenceResults())
        uids = filter(api.is_uid, uids)
        if only_uids:
            return uids
        brains = api.search({'UID': uids}, 'uid_catalog')
        return map(api.get_object, brains)

    security.declarePublic('getReferenceAnalyses')
    def getReferenceAnalyses(self):
        """ return all analyses linked to this reference sample """
        return self.objectValues('ReferenceAnalysis')

    security.declarePublic('getReferenceAnalysesService')
    def getReferenceAnalysesService(self, service_uid):
        """ return all analyses linked to this reference sample for a service """
        analyses = []
        for analysis in self.objectValues('ReferenceAnalysis'):
            if analysis.getServiceUID() == service_uid:
                analyses.append(analysis)
        return analyses

    security.declarePublic('addReferenceAnalysis')
    def addReferenceAnalysis(self, service):
        """
        Creates a new Reference Analysis object based on this Sample
        Reference, with the type passed in and associates the newly
        created object to the Analysis Service passed in.

        :param service: Object, brain or UID of the Analysis Service
        :param reference_type: type of ReferenceAnalysis, where 'b' is is
        Blank and 'c' is Control
        :type reference_type: A String
        :returns: the newly created Reference Analysis
        :rtype: string
        """
        if api.is_uid(service) or api.is_brain(service):
            return self.addReferenceAnalysis(api.get_object(service))

        if not IAnalysisService.providedBy(service):
            return None

        interim_fields = service.getInterimFields()
        analysis = _createObjectByType("ReferenceAnalysis", self, id=tmpID())
        # Copy all the values from the schema
        # TODO Add Service as a param in ReferenceAnalysis constructor and do
        #      this logic there instead of here
        discard = ['id', ]
        keys = service.Schema().keys()
        for key in keys:
            if key in discard:
                continue
            if key not in analysis.Schema().keys():
                continue
            val = service.getField(key).get(service)
            # Campbell's mental note:never ever use '.set()' directly to a
            # field. If you can't use the setter, then use the mutator in order
            # to give the value. We have realized that in some cases using
            # 'set' when the value is a string, it saves the value
            # as unicode instead of plain string.
            # analysis.getField(key).set(analysis, val)
            mutator_name = analysis.getField(key).mutator
            mutator = getattr(analysis, mutator_name)
            mutator(val)
        analysis.setAnalysisService(service)
        ref_type = self.getBlank() and 'b' or 'c'
        analysis.setReferenceType(ref_type)
        analysis.setInterimFields(interim_fields)
        analysis.unmarkCreationFlag()
        renameAfterCreation(analysis)
        return analysis


    security.declarePublic('getServices')
    def getServices(self):
        """ get all services for this Sample """
        tool = getToolByName(self, REFERENCE_CATALOG)
        services = []
        for spec in self.getReferenceResults():
            service = tool.lookupObject(spec['uid'])
            services.append(service)
        return services

    def isValid(self):
        """
        Returns if the current Reference Sample is valid. This is, the sample
        hasn't neither been expired nor disposed.
        """
        today = DateTime()
        expiry_date = self.getExpiryDate()
        if expiry_date and today > expiry_date:
            return False
        # TODO: Do We really need ExpiryDate + DateExpired? Any difference?
        date_expired = self.getDateExpired()
        if date_expired and today > date_expired:
            return False

        date_disposed = self.getDateDisposed()
        if date_disposed and today > date_disposed:
            return False

        return True

    # XXX workflow methods
    def workflow_script_expire(self):
        """ expire sample """
        self.setDateExpired(DateTime())
        self.reindexObject()

    def workflow_script_dispose(self):
        """ dispose sample """
        self.setDateDisposed(DateTime())
        self.reindexObject()

registerType(ReferenceSample, PROJECTNAME)
