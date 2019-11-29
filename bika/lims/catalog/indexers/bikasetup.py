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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from plone.indexer import indexer

from bika.lims import api
from bika.lims.interfaces import IAnalysisCategory
from bika.lims.interfaces import IAnalysisService
from bika.lims.interfaces import IBikaSetupCatalog
from bika.lims.interfaces import IHavePrice
from bika.lims.interfaces import IInstrument
from bika.lims.interfaces import ISampleTypeAwareMixin
from bika.lims.interfaces import IWorksheetTemplate


@indexer(ISampleTypeAwareMixin, IBikaSetupCatalog)
def sampletype_uids(instance):
    """Returns the list of SampleType UIDs the instance is assigned to

    This is a KeywordIndex, so it will be indexed as a list, even if only one
    SampleType can be assigned to the instance. Moreover, if the instance has no
    SampleType assigned, it returns a tuple with a None value. This allows
    searches for `MissingValue` entries too.
    """
    return instance.getSampleTypeUID() or (None, )


@indexer(ISampleTypeAwareMixin, IBikaSetupCatalog)
def sampletype_title(instance):
    """Returns a list of titles from SampleType the instance is assigned to

    If the instance has no sample type assigned, it returns a tuple with
    a None value. This allows searches for `MissingValue` entries too.
    """
    sample_type = instance.getSampleType()
    return to_title_list(sample_type)


@indexer(IAnalysisService, IBikaSetupCatalog)
def method_available_uids(instance):
    """Returns a list of Method UIDs that are available for this instance

    If the instance (AnalysisService) has InstrumentEntryOfResults set to True,
    it returns the methods available from the instruments capable to perform the
    service, as well as the methods set manually to the analysis. Otherwise, it
    returns the methods assigned manually only.

    If the instance has no available method assigned, it returns a tuple with
    a None value. This allows searches for `MissingValue` entries too.
    """
    return instance.getAvailableMethodUIDs() or (None, )


@indexer(IWorksheetTemplate, IBikaSetupCatalog)
def instrument_title(instance):
    """Returns a list of titles from SampleType the instance is assigned to

    If the instance has no instrument assigned, it returns a tuple with
    a None value. This allows searches for `MissingValue` entries too.
    """
    instrument = instance.getInstrument()
    return to_title_list(instrument)


@indexer(IHavePrice, IBikaSetupCatalog)
def price(instance):
    """Returns the price of the instance
    """
    return instance.getPrice()


@indexer(IHavePrice, IBikaSetupCatalog)
def price_total(instance):
    """Returns the total price of the instance
    """
    return instance.getTotalPrice()


@indexer(IInstrument, IBikaSetupCatalog)
def instrumenttype_title(instance):
    """Returns the title of the Instrument Type the instance is assigned to

    If the instance has no instrument type assigned, it returns a tuple with
    a None value. This allows searches for `MissingValue` entries too.
    """
    instrument_type = instance.getInstrumentType()
    return to_title_list(instrument_type)


@indexer(IAnalysisCategory, IBikaSetupCatalog)
def department_title(instance):
    """Returns the title of the Department the instance is assigned to

    If the instance has no instrument type assigned, it returns a tuple with
    a None value. This allows searches for `MissingValue` entries too.
    """
    department = instance.getDepartment()
    return to_title_list(department)


@indexer(IAnalysisService, IBikaSetupCatalog)
def point_of_capture(instance):
    """Returns the point of capture of the instance
    """
    return instance.getPointOfCapture()


def to_title_list(obj):
    if isinstance(obj, (list, tuple)):
        return map(api.get_title, obj)
    elif obj:
        return [api.get_title(obj)]
    return [None]
