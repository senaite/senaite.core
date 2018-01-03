# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import warnings
import pkg_resources

try:
    __version__ = pkg_resources.get_distribution("senaite.core").version
except TypeError:
    __version__ = pkg_resources.get_distribution("bika.lims").version
    print 'Using old distribution name: bika.lims'

# import this to create messages in the bika domain.
from zope.i18nmessageid import MessageFactory
bikaMessageFactory = MessageFactory('bika')
_ = MessageFactory('bika.lims')
from Products.Archetypes import PloneMessageFactory as PMF

# import this to log messages
import logging
logger = logging.getLogger('Bika')

from bika.lims.validators import *
from bika.lims.config import *
from bika.lims.permissions import *

from AccessControl import ModuleSecurityInfo, allow_module
from Products.Archetypes.atapi import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.utils import ContentInit, ToolInit, getToolByName
from Products.CMFPlone import PloneMessageFactory
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.GenericSetup import EXTENSION, profile_registry

allow_module('AccessControl')
allow_module('bika.lims')
allow_module('bika.lims.config')
allow_module('bika.lims.permissions')
allow_module('bika.lims.utils')
allow_module('json')
allow_module('zope.i18n.locales')
allow_module('zope.component')
allow_module('plone.registry.interfaces')

import App
debug_mode = App.config.getConfiguration().debug_mode
if debug_mode:
    allow_module('pdb')
    allow_module('pudb')

def initialize(context):

    from content.analysis import Analysis
    from content.analysiscategory import AnalysisCategory
    from content.analysisrequest import AnalysisRequest
    from content.analysisrequestsfolder import AnalysisRequestsFolder
    from content.analysisservice import AnalysisService
    from content.analysisspec import AnalysisSpec
    from content.arimport import ARImport
    from content.analysisprofile import AnalysisProfile
    from content.arreport import ARReport
    from content.artemplate import ARTemplate
    from content.attachment import Attachment
    from content.attachmenttype import AttachmentType
    from content.batch import Batch
    from content.batchfolder import BatchFolder
    from content.batchlabel import BatchLabel
    from content.bikacache import BikaCache
    from content.bikaschema import BikaSchema
    from content.bikasetup import BikaSetup
    from content.calculation import Calculation
    from content.client import Client
    from content.clientfolder import ClientFolder
    from content.contact import Contact
    from content.container import Container
    from content.containertype import ContainerType
    from content.department import Department
    from content.duplicateanalysis import DuplicateAnalysis
    from content.identifiertype import IdentifierType
    from content.instrument import Instrument
    from content.instrumentcalibration import InstrumentCalibration
    from content.instrumentcertification import InstrumentCertification
    from content.instrumentmaintenancetask import InstrumentMaintenanceTask
    from content.instrumentscheduledtask import InstrumentScheduledTask
    from content.instrumentvalidation import InstrumentValidation
    from content.instrumenttype import InstrumentType
    from content.instrumentlocation import InstrumentLocation
    from content.invoice import Invoice
    from content.invoicebatch import InvoiceBatch
    from content.invoicefolder import InvoiceFolder
    from content.labcontact import LabContact
    from content.laboratory import Laboratory
    from content.labproduct import LabProduct
    from content.manufacturer import Manufacturer
    from content.method import Method
    from content.methods import Methods
    from content.multifile import Multifile
    from content.organisation import Organisation
    from content.person import Person
    from content.preservation import Preservation
    from content.pricelist import Pricelist
    from content.pricelistfolder import PricelistFolder
    from content.referenceanalysis import ReferenceAnalysis
    from content.referencedefinition import ReferenceDefinition
    from content.referencesample import ReferenceSample
    from content.referencesamplesfolder import ReferenceSamplesFolder
    from content.rejectanalysis import RejectAnalysis
    from content.report import Report
    from content.reportfolder import ReportFolder
    from content.sample import Sample
    from content.samplecondition import SampleCondition
    from content.samplematrix import SampleMatrix
    from content.samplepartition import SamplePartition
    from content.samplepoint import SamplePoint
    from content.storagelocation import StorageLocation
    from content.samplesfolder import SamplesFolder
    from content.sampletype import SampleType
    from content.samplingdeviation import SamplingDeviation
    from content.srtemplate import SRTemplate
    from content.subgroup import SubGroup
    from content.supplier import Supplier
    from content.suppliercontact import SupplierContact
    from content.supplyorderfolder import SupplyOrderFolder
    from content.supplyorder import SupplyOrder
    from content.worksheet import Worksheet
    from content.worksheetfolder import WorksheetFolder
    from content.worksheettemplate import WorksheetTemplate
    from content.reflexrule import ReflexRule
    from content.autoimportlog import AutoImportLog

    from controlpanel.bika_analysiscategories import AnalysisCategories
    from controlpanel.bika_analysisservices import AnalysisServices
    from controlpanel.bika_analysisspecs import AnalysisSpecs
    from controlpanel.bika_analysisprofiles import AnalysisProfiles
    from controlpanel.bika_artemplates import ARTemplates
    from controlpanel.bika_attachmenttypes import AttachmentTypes
    from controlpanel.bika_batchlabels import BatchLabels
    from controlpanel.bika_calculations import Calculations
    from controlpanel.bika_containers import Containers
    from controlpanel.bika_containertypes import ContainerTypes
    from controlpanel.bika_departments import Departments
    from controlpanel.bika_identifiertypes import IdentifierTypes
    from controlpanel.bika_instruments import Instruments
    from controlpanel.bika_instrumenttypes import InstrumentTypes
    from controlpanel.bika_instrumentlocations import InstrumentLocations
    from controlpanel.bika_labcontacts import LabContacts
    from controlpanel.bika_labproducts import LabProducts
    from controlpanel.bika_manufacturers import Manufacturers
    from controlpanel.bika_preservations import Preservations
    from controlpanel.bika_referencedefinitions import ReferenceDefinitions
    from controlpanel.bika_sampleconditions import SampleConditions
    from controlpanel.bika_samplematrices import SampleMatrices
    from controlpanel.bika_samplepoints import SamplePoints
    from controlpanel.bika_storagelocations import StorageLocations
    from controlpanel.bika_sampletypes import SampleTypes
    from controlpanel.bika_samplingdeviations import SamplingDeviations
    from controlpanel.bika_srtemplates import SRTemplates
    from controlpanel.bika_subgroups import SubGroups
    from controlpanel.bika_suppliers import Suppliers
    from controlpanel.bika_worksheettemplates import WorksheetTemplates
    from controlpanel.bika_reflexrulefolder import ReflexRuleFolder

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    # Register each type with it's own Add permission
    # use ADD_CONTENT_PERMISSION as default
    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: Add %s" % (config.PROJECTNAME, atype.portal_type)
        perm = ADD_CONTENT_PERMISSIONS.get(atype.portal_type,
                                           ADD_CONTENT_PERMISSION)
        ContentInit(kind,
                    content_types      = (atype,),
                    permission         = perm,
                    extra_constructors = (constructor,),
                    fti                = ftis,
                    ).initialize(context)


def deprecated(comment=None, replacement=None):
    """
    Flags a function as deprecated. A warning will be emitted.
    :param comment: A human-friendly string, such as 'This  function
                    will be removed soon'
    :type comment: string
    :param replacement: The function to be used instead
    :type replacement: string or function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            message = "Call to deprecated function '{}.{}'".format(
                func.__module__,
                func.__name__)
            if replacement and isinstance(replacement, str):
                message += ". Use '{}' instead".format(replacement)
            elif replacement:
                message += ". Use '{}.{}' instead".format(
                 replacement.__module__,
                 replacement.__name__)
            if comment:
                message += ". {}".format(comment)
            warnings.simplefilter('always', DeprecationWarning)
            warnings.warn(message, category=DeprecationWarning, stacklevel=2)
            warnings.simplefilter('default', DeprecationWarning)
            return func(*args, **kwargs)
        return wrapper
    return decorator


class _DeprecatedClassDecorator(object):
    """ A decorator which can be used to mark symbols as deprecated.
        Emits a DeprecationWarning showing the symbol being flagged as
        deprecated. For add comments, use deprecated() instead of it
    """
    def __call__(self, symbol):
        message = "Deprecated: '%s.%s'" % \
            (symbol.__module__,
             symbol.__name__)
        warnings.warn(message, category=DeprecationWarning, stacklevel=2)
        return symbol

deprecatedsymbol = _DeprecatedClassDecorator()
del _DeprecatedClassDecorator


def enum(**enums):
    return type('Enum', (), enums)
