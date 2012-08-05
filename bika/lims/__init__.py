# import this to create messages in the bika domain.
from zope.i18nmessageid import MessageFactory
bikaMessageFactory = MessageFactory('bika')
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
allow_module('bika.lims.permissions')
allow_module('bika.lims.utils')
allow_module('json')
allow_module('pdb')
allow_module('zope.i18n.locales')

def initialize(context):

    from content.analysis import Analysis
    from content.analysiscategory import AnalysisCategory
    from content.analysisrequest import AnalysisRequest
    from content.analysisrequestsfolder import AnalysisRequestsFolder
    from content.analysisservice import AnalysisService
    from content.analysisspec import AnalysisSpec
    from content.arimport import ARImport
    from content.arimportitem import ARImportItem
    from content.analysisprofile import AnalysisProfile
    from content.artemplate import ARTemplate
    from content.attachment import Attachment
    from content.attachmenttype import AttachmentType
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
    from content.instrument import Instrument
    from content.invoice import Invoice
    from content.invoicebatch import InvoiceBatch
    from content.invoicefolder import InvoiceFolder
    from content.invoicelineitem import InvoiceLineItem
    from content.labcontact import LabContact
    from content.laboratory import Laboratory
    from content.labproduct import LabProduct
    from content.logentry import LogEntry
    from content.method import Method
    from content.methods import Methods
    from content.organisation import Organisation
    from content.person import Person
    from content.preservation import Preservation
    from content.pricelist import Pricelist
    from content.pricelistfolder import PricelistFolder
    from content.pricelistlineitem import PricelistLineItem
    from content.referenceanalysis import ReferenceAnalysis
    from content.referencedefinition import ReferenceDefinition
    from content.referencemanufacturer import ReferenceManufacturer
    from content.referencesample import ReferenceSample
    from content.referencesamplesfolder import ReferenceSamplesFolder
    from content.referencesupplier import ReferenceSupplier
    from content.report import Report
    from content.reportfolder import ReportFolder
    from content.sample import Sample
    from content.samplematrix import SampleMatrix
    from content.samplepartition import SamplePartition
    from content.samplepoint import SamplePoint
    from content.samplesfolder import SamplesFolder
    from content.sampletype import SampleType
    from content.samplingdeviation import SamplingDeviation
    from content.suppliercontact import SupplierContact
    from content.supplyorder import SupplyOrder
    from content.supplyorderitem import SupplyOrderItem
    from content.worksheet import Worksheet
    from content.worksheetfolder import WorksheetFolder
    from content.worksheettemplate import WorksheetTemplate

    from controlpanel.bika_analysiscategories import AnalysisCategories
    from controlpanel.bika_analysisservices import AnalysisServices
    from controlpanel.bika_analysisspecs import AnalysisSpecs
    from controlpanel.bika_analysisprofiles import AnalysisProfiles
    from controlpanel.bika_artemplates import ARTemplates
    from controlpanel.bika_attachmenttypes import AttachmentTypes
    from controlpanel.bika_calculations import Calculations
    from controlpanel.bika_containers import Containers
    from controlpanel.bika_containertypes import ContainerTypes
    from controlpanel.bika_departments import Departments
    from controlpanel.bika_instruments import Instruments
    from controlpanel.bika_labcontacts import LabContacts
    from controlpanel.bika_labproducts import LabProducts
    from controlpanel.bika_preservations import Preservations
    from controlpanel.bika_referencedefinitions import ReferenceDefinitions
    from controlpanel.bika_referencemanufacturers import ReferenceManufacturers
    from controlpanel.bika_referencesuppliers import ReferenceSuppliers
    from controlpanel.bika_samplematrices import SampleMatrices
    from controlpanel.bika_samplepoints import SamplePoints
    from controlpanel.bika_sampletypes import SampleTypes
    from controlpanel.bika_samplingdeviations import SamplingDeviations
    from controlpanel.bika_worksheettemplates import WorksheetTemplates

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
        utils.ContentInit(kind,
                          content_types      = (atype,),
                          permission         = perm,
                          extra_constructors = (constructor,),
                          fti                = ftis,
                          ).initialize(context)
