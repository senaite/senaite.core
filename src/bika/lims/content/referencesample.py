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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import ReferenceResultsField
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets import DateTimeWidget as bika_DateTimeWidget
from bika.lims.browser.widgets import ReferenceResultsWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IDeactivable
from bika.lims.interfaces import IReferenceSample
from DateTime import DateTime
from Products.Archetypes.atapi import registerType
from Products.Archetypes.BaseFolder import BaseFolder
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.Field import BooleanField
from Products.Archetypes.Field import ComputedField
from Products.Archetypes.Field import DateTimeField
from Products.Archetypes.Field import StringField
from Products.Archetypes.Field import TextField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import BooleanWidget
from Products.Archetypes.Widget import ComputedWidget
from Products.Archetypes.Widget import StringWidget
from Products.Archetypes.Widget import TextAreaWidget
from Products.CMFCore.utils import getToolByName
from senaite.core.browser.widgets.referencewidget import ReferenceWidget
from senaite.core.catalog import SETUP_CATALOG
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    UIDReferenceField(
        "ReferenceDefinition",
        schemata="Description",
        allowed_types=("ReferenceDefinition",),
        widget=ReferenceWidget(
            label=_(
                "label_referencesample_referencedefinition",
                default="Reference Definition"),
            description=_(
                "description_referencesample_referencedefinition",
                default="Select the reference definition for this sample"),
            catalog=SETUP_CATALOG,
            query={
                "is_active": True,
                "sort_on": "sortable_title",
                "sort_order": "ascending"
            },
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

    UIDReferenceField(
        "Manufacturer",
        schemata="Description",
        allowed_types=("Manufacturer",),
        vocabulary="getManufacturers",
        widget=ReferenceWidget(
            label=_(
                "label_referencesample_manufacturer",
                default="Manufacturer"),
            description=_(
                "description_referencesample_manufacturer",
                default="Select the manufacturer for this sample"),
            catalog=SETUP_CATALOG,
            query={
                "is_active": True,
                "sort_on": "sortable_title",
                "sort_order": "ascending"
            },
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
                    'result':'analysisspecs_validator',},
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
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from senaite.core.idserver import renameAfterCreation
        renameAfterCreation(self)

    security.declarePublic('current_date')
    def current_date(self):
        return DateTime()

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
