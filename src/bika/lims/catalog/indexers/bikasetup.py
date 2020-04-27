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

from bika.lims import api
from bika.lims.catalog.bikasetup_catalog import SETUP_CATALOG
from bika.lims.catalog.indexers import generic_listing_searchable_text
from bika.lims.interfaces import IAnalysisService
from bika.lims.interfaces import IBikaSetupCatalog
from bika.lims.interfaces import IHaveAnalysisCategory
from bika.lims.interfaces import IHaveDepartment
from bika.lims.interfaces import IHaveInstrument
from bika.lims.interfaces import IHavePrice
from bika.lims.interfaces import IInstrument
from bika.lims.interfaces import ISampleTypeAwareMixin
from plone.indexer import indexer
from Products.CMFCore.interfaces import IContentish


@indexer(ISampleTypeAwareMixin, IBikaSetupCatalog)
def sampletype_uid(instance):
    """Returns the list of SampleType UIDs the instance is assigned to

    This is a KeywordIndex, so it will be indexed as a list, even if only one
    SampleType can be assigned to the instance. Moreover, if the instance has
    no SampleType assigned, it returns a tuple with a None value. This allows
    searches for `MissingValue` entries too.
    """
    sample_type = instance.getSampleType()
    return to_keywords_list(sample_type, api.get_uid)


@indexer(ISampleTypeAwareMixin, IBikaSetupCatalog)
def sampletype_title(instance):
    """Returns a list of titles from SampleType the instance is assigned to

    If the instance has no sample type assigned, it returns a tuple with
    a None value. This allows searches for `MissingValue` entries too.
    """
    sample_type = instance.getSampleType()
    return to_keywords_list(sample_type, api.get_title)


@indexer(IAnalysisService, IBikaSetupCatalog)
def method_available_uid(instance):
    """Returns a list of Method UIDs that are available for this instance

    If the instance (AnalysisService) has InstrumentEntryOfResults set to True,
    it returns the methods available from the instruments capable to perform
    the service, as well as the methods set manually to the analysis.
    Otherwise, it returns the methods assigned manually only.

    If the instance has no available method assigned, it returns a tuple with
    a None value. This allows searches for `MissingValue` entries too.
    """
    return instance.getAvailableMethodUIDs() or (None, )


@indexer(IHaveInstrument, IBikaSetupCatalog)
def instrument_title(instance):
    """Returns a list of titles from Instrument the instance is assigned to

    If the instance has no instrument assigned, it returns a tuple with
    a None value. This allows searches for `MissingValue` entries too.
    """
    instrument = instance.getInstrument()
    return to_keywords_list(instrument, api.get_title)


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
    """Returns a list of Instrument Type titles the instance is assigned to
    """
    instrument_type = instance.getInstrumentType()
    return to_keywords_list(instrument_type, api.get_title)


@indexer(IHaveDepartment, IBikaSetupCatalog)
def department_uid(instance):
    """Returns a list of Department UIDs the instance is assigned to
    """
    department = instance.getDepartment()
    return to_keywords_list(department, api.get_uid)


@indexer(IHaveDepartment, IBikaSetupCatalog)
def department_title(instance):
    """Returns the title of the Department the instance is assigned to
    """
    department = instance.getDepartment()
    return to_keywords_list(department, api.get_title)


@indexer(IAnalysisService, IBikaSetupCatalog)
def point_of_capture(instance):
    """Returns the point of capture of the instance
    """
    return instance.getPointOfCapture()


@indexer(IContentish, IBikaSetupCatalog)
def listing_searchable_text(instance):
    """ Retrieves all the values of metadata columns in the catalog for
    wildcard searches
    :return: all metadata values joined in a string
    """
    exclude = ["getObjPositionInParent", ]

    # Additional non-metadata fields to include in the index
    include = ["getCalculation"
               "getDepartment",
               "getInstrument",
               "getInstrumentType",
               "getSamplePoint"
               "getSampleType",
               "getSupplier",
               "getManufacturer", ]

    return generic_listing_searchable_text(instance, SETUP_CATALOG,
                                           exclude_field_names=exclude,
                                           include_field_names=include)


@indexer(IHaveAnalysisCategory, IBikaSetupCatalog)
def category_uid(instance):
    """Returns a list of Category UIDs the instance is assigned to
    """
    category = instance.getCategory()
    return to_keywords_list(category, api.get_uid)


def to_keywords_list(obj, func):
    if isinstance(obj, (list, tuple)):
        return map(func, obj)
    elif obj:
        return [func(obj)]
    return [None]
