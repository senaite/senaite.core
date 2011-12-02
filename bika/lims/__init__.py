# import this to create messages in the bika domain.
from zope.i18nmessageid import MessageFactory
bikaMessageFactory = MessageFactory('bika')
# import this to log messages
import logging
logger = logging.getLogger('Bika')

from bika.lims.validators import *
from bika.lims.config import *

from AccessControl import ModuleSecurityInfo, allow_module
from Products.Archetypes.atapi import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.utils import ContentInit, ToolInit, getToolByName
from Products.CMFPlone import PloneMessageFactory
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.GenericSetup import EXTENSION, profile_registry

allow_module('bika.lims')
allow_module('AccessControl')

def initialize(context):

    from content.Invoice import Invoice
    from content.InvoiceBatch import InvoiceBatch
    from content.InvoiceFolder import InvoiceFolder
    from content.InvoiceLineItem import InvoiceLineItem
    from content.MethodLogEntry import MethodLogEntry
    from content.Pricelist import Pricelist
    from content.PricelistFolder import PricelistFolder
    from content.PricelistLineItem import PricelistLineItem
    from content.SupplierContact import SupplierContact
    from content.analysis  import Analysis
    from content.analysiscategory import AnalysisCategory
    from content.analysisrequest import AnalysisRequest
    from content.analysisrequestsfolder import AnalysisRequestsFolder
    from content.analysisservice import AnalysisService
    from content.analysisspec import AnalysisSpec
    from content.arimport import ARImport
    from content.arimportitem import ARImportItem
    from content.arprofile import ARProfile
    from content.attachment import Attachment
    from content.attachmenttype import AttachmentType
    from content.bikaschema import BikaSchema
    from content.bikasetup import BikaSetup
    from content.calculation import Calculation
    from content.client import Client
    from content.clientfolder import ClientFolder
    from content.contact import Contact
    from content.department import Department
    from content.duplicateanalysis import DuplicateAnalysis
    from content.instrument import Instrument
    from content.labcontact import LabContact
    from content.laboratory import Laboratory
    from content.labproduct import LabProduct
    from content.method import Method
    from content.organisation import Organisation
    from content.person import Person
    from content.referenceanalysis import ReferenceAnalysis
    from content.referencedefinition import ReferenceDefinition
    from content.referencemanufacturer import ReferenceManufacturer
    from content.referencesample import ReferenceSample
    from content.referencesamplesfolder import ReferenceSamplesFolder
    from content.referencesupplier import ReferenceSupplier
    from content.rejectanalysis import RejectAnalysis
    from content.reports import Reports
    from content.sample import Sample
    from content.samplepoint import SamplePoint
    from content.samplesfolder import SamplesFolder
    from content.sampletype import SampleType
    from content.supplyorder import SupplyOrder
    from content.supplyorderitem import SupplyOrderItem
    from content.worksheet import Worksheet
    from content.worksheetfolder import WorksheetFolder
    from content.worksheettemplate import WorksheetTemplate

    from controlpanel.bika_analysiscategories import AnalysisCategories
    from controlpanel.bika_analysisservices import AnalysisServices
    from controlpanel.bika_analysisspecs import AnalysisSpecs
    from controlpanel.bika_arprofiles import ARProfiles
    from controlpanel.bika_attachmenttypes import AttachmentTypes
    from controlpanel.bika_calculations import Calculations
    from controlpanel.bika_departments import Departments
    from controlpanel.bika_instruments import Instruments
    from controlpanel.bika_labcontacts import LabContacts
    from controlpanel.bika_labproducts import LabProducts
    from controlpanel.bika_methods import Methods
    from controlpanel.bika_referencedefinitions import ReferenceDefinitions
    from controlpanel.bika_referencemanufacturers import ReferenceManufacturers
    from controlpanel.bika_referencesuppliers import ReferenceSuppliers
    from controlpanel.bika_samplepoints import SamplePoints
    from controlpanel.bika_sampletypes import SampleTypes
    from controlpanel.bika_worksheettemplates import WorksheetTemplates

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    ContentInit(
        PROJECTNAME,
        content_types = content_types,
        permission = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti = ftis,
        ).initialize(context)

