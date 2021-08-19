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
from bika.lims.config import *  # noqa
# from bika.lims.permissions import *  # noqa
from bika.lims.validators import *  # noqa
from Products.Archetypes import PloneMessageFactory as PMF  # noqa


def initialize(context):
    logger.info("*** Initializing BIKA.LIMS ***")
    # DELETE AFTER 2.0.0
    from bika.lims.content.supplyorder import SupplyOrder  # noqa
    from bika.lims.content.supplyorderfolder import SupplyOrderFolder  # noqa
    # /DELETE AFTER 2.0.0
    from bika.lims.content.analysis import Analysis  # noqa
    from bika.lims.content.analysiscategory import AnalysisCategory  # noqa
    from bika.lims.content.analysisprofile import AnalysisProfile  # noqa
    from bika.lims.content.analysisrequest import AnalysisRequest  # noqa
    from bika.lims.content.analysisrequestsfolder import AnalysisRequestsFolder  # noqa
    from bika.lims.content.analysisservice import AnalysisService  # noqa
    from bika.lims.content.analysisspec import AnalysisSpec  # noqa
    from bika.lims.content.arreport import ARReport  # noqa
    from bika.lims.content.artemplate import ARTemplate  # noqa
    from bika.lims.content.attachment import Attachment  # noqa
    from bika.lims.content.attachmenttype import AttachmentType  # noqa
    from bika.lims.content.autoimportlog import AutoImportLog  # noqa
    from bika.lims.content.batch import Batch  # noqa
    from bika.lims.content.batchfolder import BatchFolder  # noqa
    from bika.lims.content.batchlabel import BatchLabel  # noqa
    from bika.lims.content.bikaschema import BikaSchema  # noqa
    from bika.lims.content.bikasetup import BikaSetup  # noqa
    from bika.lims.content.calculation import Calculation  # noqa
    from bika.lims.content.client import Client  # noqa
    from bika.lims.content.clientfolder import ClientFolder  # noqa
    from bika.lims.content.contact import Contact  # noqa
    from bika.lims.content.container import Container  # noqa
    from bika.lims.content.containertype import ContainerType  # noqa
    from bika.lims.content.department import Department  # noqa
    from bika.lims.content.duplicateanalysis import DuplicateAnalysis  # noqa
    from bika.lims.content.instrument import Instrument  # noqa
    from bika.lims.content.instrumentcalibration import InstrumentCalibration  # noqa
    from bika.lims.content.instrumentcertification import InstrumentCertification  # noqa
    from bika.lims.content.instrumentlocation import InstrumentLocation  # noqa
    from bika.lims.content.instrumentmaintenancetask import InstrumentMaintenanceTask  # noqa
    from bika.lims.content.instrumentscheduledtask import InstrumentScheduledTask  # noqa
    from bika.lims.content.instrumenttype import InstrumentType  # noqa
    from bika.lims.content.instrumentvalidation import InstrumentValidation  # noqa
    from bika.lims.content.invoice import Invoice  # noqa
    from bika.lims.content.labcontact import LabContact  # noqa
    from bika.lims.content.laboratory import Laboratory  # noqa
    from bika.lims.content.labproduct import LabProduct  # noqa
    from bika.lims.content.manufacturer import Manufacturer  # noqa
    from bika.lims.content.method import Method  # noqa
    from bika.lims.content.methods import Methods  # noqa
    from bika.lims.content.multifile import Multifile  # noqa
    from bika.lims.content.organisation import Organisation  # noqa
    from bika.lims.content.person import Person  # noqa
    from bika.lims.content.preservation import Preservation  # noqa
    from bika.lims.content.pricelist import Pricelist  # noqa
    from bika.lims.content.pricelistfolder import PricelistFolder  # noqa
    from bika.lims.content.referenceanalysis import ReferenceAnalysis  # noqa
    from bika.lims.content.referencedefinition import ReferenceDefinition  # noqa
    from bika.lims.content.referencesample import ReferenceSample  # noqa
    from bika.lims.content.referencesamplesfolder import ReferenceSamplesFolder  # noqa
    from bika.lims.content.rejectanalysis import RejectAnalysis  # noqa
    from bika.lims.content.report import Report  # noqa
    from bika.lims.content.reportfolder import ReportFolder  # noqa
    from bika.lims.content.samplecondition import SampleCondition  # noqa
    from bika.lims.content.samplematrix import SampleMatrix  # noqa
    from bika.lims.content.samplepoint import SamplePoint  # noqa
    from bika.lims.content.sampletype import SampleType  # noqa
    from bika.lims.content.samplingdeviation import SamplingDeviation  # noqa
    from bika.lims.content.storagelocation import StorageLocation  # noqa
    from bika.lims.content.subgroup import SubGroup  # noqa
    from bika.lims.content.supplier import Supplier  # noqa
    from bika.lims.content.suppliercontact import SupplierContact  # noqa
    from bika.lims.content.worksheet import Worksheet  # noqa
    from bika.lims.content.worksheetfolder import WorksheetFolder  # noqa
    from bika.lims.content.worksheettemplate import WorksheetTemplate  # noqa

    from bika.lims.controlpanel.auditlog import AuditLog  # noqa
    from bika.lims.controlpanel.bika_analysiscategories import AnalysisCategories  # noqa
    from bika.lims.controlpanel.bika_analysisprofiles import AnalysisProfiles  # noqa
    from bika.lims.controlpanel.bika_analysisservices import AnalysisServices  # noqa
    from bika.lims.controlpanel.bika_analysisspecs import AnalysisSpecs  # noqa
    from bika.lims.controlpanel.bika_artemplates import ARTemplates  # noqa
    from bika.lims.controlpanel.bika_attachmenttypes import AttachmentTypes  # noqa
    from bika.lims.controlpanel.bika_batchlabels import BatchLabels  # noqa
    from bika.lims.controlpanel.bika_calculations import Calculations  # noqa
    from bika.lims.controlpanel.bika_containers import Containers  # noqa
    from bika.lims.controlpanel.bika_containertypes import ContainerTypes  # noqa
    from bika.lims.controlpanel.bika_departments import Departments  # noqa
    from bika.lims.controlpanel.bika_instrumentlocations import InstrumentLocations  # noqa
    from bika.lims.controlpanel.bika_instruments import Instruments  # noqa
    from bika.lims.controlpanel.bika_instrumenttypes import InstrumentTypes  # noqa
    from bika.lims.controlpanel.bika_labcontacts import LabContacts  # noqa
    from bika.lims.controlpanel.bika_labproducts import LabProducts  # noqa
    from bika.lims.controlpanel.bika_manufacturers import Manufacturers  # noqa
    from bika.lims.controlpanel.bika_preservations import Preservations  # noqa
    from bika.lims.controlpanel.bika_referencedefinitions import ReferenceDefinitions  # noqa
    from bika.lims.controlpanel.bika_sampleconditions import SampleConditions  # noqa
    from bika.lims.controlpanel.bika_samplematrices import SampleMatrices  # noqa
    from bika.lims.controlpanel.bika_samplepoints import SamplePoints  # noqa
    from bika.lims.controlpanel.bika_sampletypes import SampleTypes  # noqa
    from bika.lims.controlpanel.bika_samplingdeviations import SamplingDeviations  # noqa
    from bika.lims.controlpanel.bika_storagelocations import StorageLocations  # noqa
    from bika.lims.controlpanel.bika_subgroups import SubGroups  # noqa
    from bika.lims.controlpanel.bika_suppliers import Suppliers  # noqa
    from bika.lims.controlpanel.bika_worksheettemplates import WorksheetTemplates  # noqa

    from bika.lims import permissions

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME), PROJECTNAME)

    # Register each type with it's own Add permission
    # use "Add portal content" as default
    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: Add %s" % (PROJECTNAME, atype.portal_type)
        perm_name = "Add{}".format(atype.portal_type)
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
