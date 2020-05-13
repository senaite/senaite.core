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

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.Field import StringField
from Products.Archetypes.public import Schema
from Products.Archetypes.public import registerType
from plone.app.blob.field import BlobField
from zope.interface import implements

from bika.lims import api
from bika.lims.config import PROJECTNAME
from bika.lims.config import STD_TYPES
from bika.lims.content.abstractanalysis import AbstractAnalysis
from bika.lims.content.abstractanalysis import schema
from bika.lims.content.analysisspec import ResultsRangeDict
from bika.lims.interfaces import IReferenceAnalysis

schema = schema.copy() + Schema((
    StringField(
        "ReferenceType",
        vocabulary=STD_TYPES,
    ),
    BlobField(
        "RetractedAnalysesPdfReport",
    ),
    StringField(
        "ReferenceAnalysesGroupID",
    )
))


class ReferenceAnalysis(AbstractAnalysis):
    """Reference Analysis Content
    """
    implements(IReferenceAnalysis)
    security = ClassSecurityInfo()
    schema = schema

    @security.public
    def getPrice(self):
        """Return the price

        :return: the price (without VAT or Member Discount) in decimal format
        """
        field = self.getField("Price")
        return field.get(self)

    @security.public
    def getSupplier(self):
        """ Returns the Supplier of the ReferenceSample this ReferenceAnalysis
        refers to
        """
        sample = self.getSample()
        if sample:
            return sample.aq_parent

    @security.public
    def getSupplierUID(self):
        supplier = self.getSupplier()
        if supplier:
            return supplier.UID()

    @security.public
    def getSample(self):
        """ Returns the ReferenceSample this ReferenceAnalysis refers to
        Delegates to self.aq_parent
        """
        return self.aq_parent

    @security.public
    def getDueDate(self):
        """Used to populate getDueDate index and metadata.
        This very simply returns the expiry date of the parent reference sample.
        """
        sample = self.getSample()
        if sample:
            return sample.getExpiryDate()

    @security.public
    def setResult(self, value):
        # Always update ResultCapture date when this field is modified
        self.setResultCaptureDate(DateTime())
        # Ensure result integrity regards to None, empty and 0 values
        val = str('' if not value and value != 0 else value).strip()
        self.getField('Result').set(self, val)

    def getReferenceResults(self):
        """
        It is used as metacolumn
        """
        return self.getSample().getReferenceResults()

    @security.public
    def getResultsRange(self):
        """Returns the valid result range for this reference analysis based on
        the results ranges defined in the Reference Sample from which this
        analysis has been created.

        A Reference Analysis (control or blank) will be considered out of range
        if its results does not match with the result defined on its parent
        Reference Sample, with the % error as the margin of error, that will be
        used to set the range's min and max values
        :return: A dictionary with the keys min and max
        :rtype: dict
        """
        specs = ResultsRangeDict(uid=api.get_uid(self),
                                 keyword=self.getKeyword(),
                                 result="")
        sample = self.getSample()
        if not sample:
            return specs

        service_uid = self.getServiceUID()
        sample_range = sample.getResultsRangeDict()
        return sample_range.get(service_uid, specs)

    def getInstrumentUID(self):
        """
        It is a metacolumn.
        Returns the same value as the service.
        """
        instrument = self.getInstrument()
        if not instrument:
            return None
        return instrument.UID()

    def getServiceDefaultInstrumentUID(self):
        """
        It is used as a metacolumn.
        Returns the default service's instrument UID
        """
        ins = self.getInstrument()
        if ins:
            return ins.UID()
        return ''

    def getServiceDefaultInstrumentTitle(self):
        """
        It is used as a metacolumn.
        Returns the default service's instrument UID
        """
        ins = self.getInstrument()
        if ins:
            return ins.Title()
        return ''

    def getServiceDefaultInstrumentURL(self):
        """
        It is used as a metacolumn.
        Returns the default service's instrument UID
        """
        ins = self.getInstrument()
        if ins:
            return ins.absolute_url_path()
        return ''

    def getDependencies(self, with_retests=False):
        """It doesn't make sense for a ReferenceAnalysis to use
        dependencies, since them are only used in calculations for
        routine analyses
        """
        return []

    def getDependents(self, with_retests=False, recursive=False):
        """It doesn't make sense for a ReferenceAnalysis to use
        dependents, since them are only used in calculations for
        routine analyses
        """
        return []


registerType(ReferenceAnalysis, PROJECTNAME)
