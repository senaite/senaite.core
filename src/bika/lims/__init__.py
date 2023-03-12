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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

import logging
import warnings

import App
from AccessControl import allow_module
from zope.i18nmessageid import MessageFactory
from Products.Archetypes.atapi import listTypes
from Products.Archetypes.atapi import process_types
from Products.CMFCore.permissions import AddPortalContent
from Products.CMFCore.utils import ContentInit

PROJECTNAME = "bika.lims"

# senaite message factory
senaiteMessageFactory = MessageFactory("senaite.core")
# BBB
bikaMessageFactory = senaiteMessageFactory
_ = senaiteMessageFactory

# import this to log messages
logger = logging.getLogger("senaite.core")

debug_mode = App.config.getConfiguration().debug_mode
if debug_mode:
    allow_module("pdb")

# Implicit module imports used by others
# XXX Refactor these dependencies to explicit imports!
from bika.lims.config import *
# from bika.lims.permissions import *
from bika.lims.validators import *
from Products.Archetypes import PloneMessageFactory as PMF


def initialize(context):
    logger.info("*** Initializing BIKA.LIMS ***")
    from bika.lims.content.analysis import Analysis
    from bika.lims.content.analysiscategory import AnalysisCategory
    from bika.lims.content.analysisprofile import AnalysisProfile
    from bika.lims.content.analysisrequest import AnalysisRequest
    from bika.lims.content.analysisrequestsfolder import AnalysisRequestsFolder
    from bika.lims.content.analysisservice import AnalysisService
    from bika.lims.content.analysisspec import AnalysisSpec
    from bika.lims.content.arreport import ARReport
    from bika.lims.content.artemplate import ARTemplate
    from bika.lims.content.attachment import Attachment
    from bika.lims.content.attachmenttype import AttachmentType
    from bika.lims.content.autoimportlog import AutoImportLog
    from bika.lims.content.batch import Batch
    from bika.lims.content.batchfolder import BatchFolder
    from bika.lims.content.batchlabel import BatchLabel
    from bika.lims.content.bikaschema import BikaSchema
    from bika.lims.content.bikasetup import BikaSetup
    from bika.lims.content.calculation import Calculation
    from bika.lims.content.client import Client
    from bika.lims.content.clientfolder import ClientFolder
    from bika.lims.content.contact import Contact
    from bika.lims.content.container import Container
    from bika.lims.content.containertype import ContainerType
    from bika.lims.content.department import Department
    from bika.lims.content.duplicateanalysis import DuplicateAnalysis
    from bika.lims.content.instrument import Instrument
    from bika.lims.content.instrumentcalibration import InstrumentCalibration
    from bika.lims.content.instrumentcertification import InstrumentCertification
    from bika.lims.content.instrumentlocation import InstrumentLocation
    from bika.lims.content.instrumentmaintenancetask import InstrumentMaintenanceTask
    from bika.lims.content.instrumentscheduledtask import InstrumentScheduledTask
    from bika.lims.content.instrumenttype import InstrumentType
    from bika.lims.content.instrumentvalidation import InstrumentValidation
    from bika.lims.content.invoice import Invoice
    from bika.lims.content.labcontact import LabContact
    from bika.lims.content.laboratory import Laboratory
    from bika.lims.content.labproduct import LabProduct
    from bika.lims.content.manufacturer import Manufacturer
    from bika.lims.content.method import Method
    from bika.lims.content.methods import Methods
    from bika.lims.content.multifile import Multifile
    from bika.lims.content.organisation import Organisation
    from bika.lims.content.person import Person
    from bika.lims.content.preservation import Preservation
    from bika.lims.content.pricelist import Pricelist
    from bika.lims.content.pricelistfolder import PricelistFolder
    from bika.lims.content.referenceanalysis import ReferenceAnalysis
    from bika.lims.content.referencedefinition import ReferenceDefinition
    from bika.lims.content.referencesample import ReferenceSample
    from bika.lims.content.referencesamplesfolder import ReferenceSamplesFolder
    from bika.lims.content.rejectanalysis import RejectAnalysis
    from bika.lims.content.report import Report
    from bika.lims.content.reportfolder import ReportFolder
    from bika.lims.content.samplecondition import SampleCondition
    from bika.lims.content.samplematrix import SampleMatrix
    from bika.lims.content.samplepoint import SamplePoint
    from bika.lims.content.sampletype import SampleType
    from bika.lims.content.samplingdeviation import SamplingDeviation
    from bika.lims.content.storagelocation import StorageLocation
    from bika.lims.content.subgroup import SubGroup
    from bika.lims.content.supplier import Supplier
    from bika.lims.content.suppliercontact import SupplierContact
    from bika.lims.content.worksheet import Worksheet
    from bika.lims.content.worksheetfolder import WorksheetFolder
    from bika.lims.content.worksheettemplate import WorksheetTemplate

    from bika.lims.controlpanel.auditlog import AuditLog
    from bika.lims.controlpanel.bika_analysiscategories import AnalysisCategories
    from bika.lims.controlpanel.bika_analysisprofiles import AnalysisProfiles
    from bika.lims.controlpanel.bika_analysisservices import AnalysisServices
    from bika.lims.controlpanel.bika_analysisspecs import AnalysisSpecs
    from bika.lims.controlpanel.bika_artemplates import ARTemplates
    from bika.lims.controlpanel.bika_attachmenttypes import AttachmentTypes
    from bika.lims.controlpanel.bika_batchlabels import BatchLabels
    from bika.lims.controlpanel.bika_calculations import Calculations
    from bika.lims.controlpanel.bika_containers import Containers
    from bika.lims.controlpanel.bika_containertypes import ContainerTypes
    from bika.lims.controlpanel.bika_departments import Departments
    from bika.lims.controlpanel.bika_instrumentlocations import InstrumentLocations
    from bika.lims.controlpanel.bika_instruments import Instruments
    from bika.lims.controlpanel.bika_instrumenttypes import InstrumentTypes
    from bika.lims.controlpanel.bika_labcontacts import LabContacts
    from bika.lims.controlpanel.bika_labproducts import LabProducts
    from bika.lims.controlpanel.bika_manufacturers import Manufacturers
    from bika.lims.controlpanel.bika_preservations import Preservations
    from bika.lims.controlpanel.bika_referencedefinitions import ReferenceDefinitions
    from bika.lims.controlpanel.bika_sampleconditions import SampleConditions
    from bika.lims.controlpanel.bika_samplematrices import SampleMatrices
    from bika.lims.controlpanel.bika_samplepoints import SamplePoints
    from bika.lims.controlpanel.bika_sampletypes import SampleTypes
    from bika.lims.controlpanel.bika_samplingdeviations import SamplingDeviations
    from bika.lims.controlpanel.bika_storagelocations import StorageLocations
    from bika.lims.controlpanel.bika_subgroups import SubGroups
    from bika.lims.controlpanel.bika_suppliers import Suppliers
    from bika.lims.controlpanel.bika_worksheettemplates import WorksheetTemplates

    from bika.lims import permissions
    from senaite.core import permissions as core_permissions

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME), PROJECTNAME)

    # Register each type with it's own Add permission
    # use "Add portal content" as default
    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: Add %s" % (PROJECTNAME, atype.portal_type)
        perm_name = "Add{}".format(atype.portal_type)
        # check first if the permission is set in senaite.core
        perm = getattr(core_permissions, perm_name, None)
        if perm is None:
            # check bika.lims.permissions or use fallback permission
            perm = getattr(permissions, perm_name, AddPortalContent)
        ContentInit(kind,
                    content_types=(atype,),
                    permission=perm,
                    extra_constructors=(constructor, ),
                    fti=ftis,
                    ).initialize(context)


def deprecated(comment=None, replacement=None):
    """Flags a function as deprecated. A warning will be emitted.

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
    """A decorator which can be used to mark symbols as deprecated.

    Emits a DeprecationWarning showing the symbol being flagged as deprecated.
    For add comments, use deprecated() instead of it
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
    return type("Enum", (), enums)
