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

import logging
import warnings

import App
from AccessControl import allow_module
from bika.lims import permissions
from Products.Archetypes.atapi import listTypes
from Products.Archetypes.atapi import process_types
from Products.CMFCore.utils import ContentInit
from zope.i18nmessageid import MessageFactory
from Products.CMFCore.permissions import AddPortalContent

PROJECTNAME = "bika.lims"

# senaite message factory
senaiteMessageFactory = MessageFactory("senaite.core")
# BBB
bikaMessageFactory = senaiteMessageFactory
_ = senaiteMessageFactory

# import this to log messages
logger = logging.getLogger("senaite.core")

# XXX: Do we really need all of these in templates?
allow_module("AccessControl")
allow_module("bika.lims")
allow_module("bika.lims.config")
allow_module("bika.lims.permissions")
allow_module("bika.lims.utils")
allow_module("json")
allow_module("zope.i18n.locales")
allow_module("zope.component")
allow_module("plone.registry.interfaces")

debug_mode = App.config.getConfiguration().debug_mode
if debug_mode:
    allow_module("pdb")

# Implicit module imports used by others
# XXX Refactor these dependencies to explicit imports!
from bika.lims.config import *  # noqa
from bika.lims.permissions import *  # noqa
from bika.lims.validators import *  # noqa
from Products.Archetypes import PloneMessageFactory as PMF  # noqa


def initialize(context):

    from content.analysis import Analysis  # noqa
    from content.analysiscategory import AnalysisCategory  # noqa
    from content.analysisprofile import AnalysisProfile  # noqa
    from content.analysisrequest import AnalysisRequest  # noqa
    from content.analysisrequestsfolder import AnalysisRequestsFolder  # noqa
    from content.analysisservice import AnalysisService  # noqa
    from content.analysisspec import AnalysisSpec  # noqa
    from content.arreport import ARReport  # noqa
    from content.artemplate import ARTemplate  # noqa
    from content.attachment import Attachment  # noqa
    from content.attachmenttype import AttachmentType  # noqa
    from content.autoimportlog import AutoImportLog  # noqa
    from content.batch import Batch  # noqa
    from content.batchfolder import BatchFolder  # noqa
    from content.batchlabel import BatchLabel  # noqa
    from content.bikaschema import BikaSchema  # noqa
    from content.bikasetup import BikaSetup  # noqa
    from content.calculation import Calculation  # noqa
    from content.client import Client  # noqa
    from content.clientfolder import ClientFolder  # noqa
    from content.contact import Contact  # noqa
    from content.container import Container  # noqa
    from content.containertype import ContainerType  # noqa
    from content.department import Department  # noqa
    from content.duplicateanalysis import DuplicateAnalysis  # noqa
    from content.identifiertype import IdentifierType  # noqa
    from content.instrument import Instrument  # noqa
    from content.instrumentcalibration import InstrumentCalibration  # noqa
    from content.instrumentcertification import InstrumentCertification  # noqa
    from content.instrumentlocation import InstrumentLocation  # noqa
    from content.instrumentmaintenancetask import InstrumentMaintenanceTask  # noqa
    from content.instrumentscheduledtask import InstrumentScheduledTask  # noqa
    from content.instrumenttype import InstrumentType  # noqa
    from content.instrumentvalidation import InstrumentValidation  # noqa
    from content.invoice import Invoice  # noqa
    from content.labcontact import LabContact  # noqa
    from content.laboratory import Laboratory  # noqa
    from content.labproduct import LabProduct  # noqa
    from content.manufacturer import Manufacturer  # noqa
    from content.method import Method  # noqa
    from content.methods import Methods  # noqa
    from content.multifile import Multifile  # noqa
    from content.organisation import Organisation  # noqa
    from content.person import Person  # noqa
    from content.preservation import Preservation  # noqa
    from content.pricelist import Pricelist  # noqa
    from content.pricelistfolder import PricelistFolder  # noqa
    from content.referenceanalysis import ReferenceAnalysis  # noqa
    from content.referencedefinition import ReferenceDefinition  # noqa
    from content.referencesample import ReferenceSample  # noqa
    from content.referencesamplesfolder import ReferenceSamplesFolder  # noqa
    from content.reflexrule import ReflexRule  # noqa
    from content.rejectanalysis import RejectAnalysis  # noqa
    from content.report import Report  # noqa
    from content.reportfolder import ReportFolder  # noqa
    from content.samplecondition import SampleCondition  # noqa
    from content.samplematrix import SampleMatrix  # noqa
    from content.samplepoint import SamplePoint  # noqa
    from content.sampletype import SampleType  # noqa
    from content.samplingdeviation import SamplingDeviation  # noqa
    from content.storagelocation import StorageLocation  # noqa
    from content.subgroup import SubGroup  # noqa
    from content.supplier import Supplier  # noqa
    from content.suppliercontact import SupplierContact  # noqa
    from content.supplyorder import SupplyOrder  # noqa
    from content.supplyorderfolder import SupplyOrderFolder  # noqa
    from content.worksheet import Worksheet  # noqa
    from content.worksheetfolder import WorksheetFolder  # noqa
    from content.worksheettemplate import WorksheetTemplate  # noqa

    from controlpanel.auditlog import AuditLog  # noqa
    from controlpanel.bika_analysiscategories import AnalysisCategories  # noqa
    from controlpanel.bika_analysisprofiles import AnalysisProfiles  # noqa
    from controlpanel.bika_analysisservices import AnalysisServices  # noqa
    from controlpanel.bika_analysisspecs import AnalysisSpecs  # noqa
    from controlpanel.bika_artemplates import ARTemplates  # noqa
    from controlpanel.bika_attachmenttypes import AttachmentTypes  # noqa
    from controlpanel.bika_batchlabels import BatchLabels  # noqa
    from controlpanel.bika_calculations import Calculations  # noqa
    from controlpanel.bika_containers import Containers  # noqa
    from controlpanel.bika_containertypes import ContainerTypes  # noqa
    from controlpanel.bika_departments import Departments  # noqa
    from controlpanel.bika_identifiertypes import IdentifierTypes  # noqa
    from controlpanel.bika_instrumentlocations import InstrumentLocations  # noqa
    from controlpanel.bika_instruments import Instruments  # noqa
    from controlpanel.bika_instrumenttypes import InstrumentTypes  # noqa
    from controlpanel.bika_labcontacts import LabContacts  # noqa
    from controlpanel.bika_labproducts import LabProducts  # noqa
    from controlpanel.bika_manufacturers import Manufacturers  # noqa
    from controlpanel.bika_preservations import Preservations  # noqa
    from controlpanel.bika_referencedefinitions import ReferenceDefinitions  # noqa
    from controlpanel.bika_reflexrulefolder import ReflexRuleFolder  # noqa
    from controlpanel.bika_sampleconditions import SampleConditions  # noqa
    from controlpanel.bika_samplematrices import SampleMatrices  # noqa
    from controlpanel.bika_samplepoints import SamplePoints  # noqa
    from controlpanel.bika_sampletypes import SampleTypes  # noqa
    from controlpanel.bika_samplingdeviations import SamplingDeviations  # noqa
    from controlpanel.bika_storagelocations import StorageLocations  # noqa
    from controlpanel.bika_subgroups import SubGroups  # noqa
    from controlpanel.bika_suppliers import Suppliers  # noqa
    from controlpanel.bika_worksheettemplates import WorksheetTemplates  # noqa

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

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
