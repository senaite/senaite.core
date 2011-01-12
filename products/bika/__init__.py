"""BIKA - A lab information management system

$Id: __init__.py 2580 2010-12-03 19:11:40Z anneline $
"""
from Products.Archetypes.atapi import process_types, listTypes
from Products.CMFCore import utils

from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.utils import ContentInit, ToolInit
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.GenericSetup import EXTENSION, profile_registry

from content import *
import Client, AnalysisRequest, Contact, Sample, Attachment, Analysis, \
       AnalysisSpec, ARProfile, ARImport, ARImportItem, Order, OrderItem, \
       Worksheet, WorksheetFolder, DuplicateAnalysis, RejectAnalysis, \
       StandardSupplierFolder, StandardSupplier, StandardSample, \
       StandardAnalysis, SupplierContact
import InvoiceFolder, InvoiceBatch, Invoice, InvoiceLineItem
import MethodFolder, Method, MethodLogEntry
import PricelistFolder, Pricelist, PricelistLineItem
import FixedPointField, AnalysesField, AnalysesWidget, ReferenceBrowserListingWidget
import AnalysisService, AnalysisCategory, Department, LabContact, \
       CalculationType, AttachmentType, Instrument, LabAnalysisSpec, \
       LabARProfile, LabProduct, ClientCategory, ClientStatus, \
       ClientPublicationPreference, ClientInvoicePreference, SampleType, \
       StandardManufacturer, SamplePoint, StandardStock, WorksheetTemplate, \
       Laboratory, BikaSettings
import Tools

from config import PROJECTNAME

#OrderWorkflow
#AnalysisWorkflow
#SampleWorkflow
#StandardSampleWorkflow
#ARImportWorkflow
#WorksheetWorkflow
#WorksheetAnalysisWorkflow
#StandardAnalysisWorkflow



from Products.bika.config import SKINS_DIR, GLOBALS, PROJECTNAME
from Products.bika.config import ADD_CONTENT_PERMISSION, BIKA_PERMISSIONS

from AccessControl import ModuleSecurityInfo, allow_module
#ModuleSecurityInfo('Products.bika.Extensions.post_plone_install').declarePublic('run')

registerDirectory(SKINS_DIR, GLOBALS)

allow_module('Products.bika.stats')
allow_module('Products.bika.pstat')
allow_module('whrandom')
allow_module('math')
allow_module('re')
allow_module('Products.bika.fixSchema')

def initialize(context):
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    ContentInit(
        PROJECTNAME + ' Content',
        content_types = content_types,
        permission = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti = ftis,
        ).initialize(context)

    tools = (
        Tools.ServicesTool,
        Tools.CategoriesTool,
        Tools.DepartmentsTool,
        Tools.LabContactsTool,
        Tools.AttachmentTypesTool,
        Tools.CalcTypesTool,
        Tools.MethodsTool,
        Tools.InstrumentsTool,
        Tools.LabSpecsTool,
        Tools.LabProfilesTool,
        Tools.ProductsTool,
        Tools.ClientStatusTool,
        Tools.ClientCategoriesTool,
        Tools.PublicationPreferenceTool,
        Tools.InvoicePreferenceTool,
        Tools.SampleTypesTool,
        Tools.StandardManufacturersTool,
        Tools.SamplePointsTool,
        Tools.StandardStocksTool,
        Tools.WorksheetTemplatesTool,
        Tools.LabInfoTool,
        Tools.SettingsTool,
        Tools.IDTool,
        Tools.InstrumentImportTool,
        Tools.ARImportTool,
        Tools.ARExportTool,
        Tools.ServicesExportTool,
        Tools.ProfilesExportTool,
        Tools.PDFBuildTool,
        Tools.AnalysisResetTool,
    )

    ToolInit(
        PROJECTNAME + ' Tools',
        tools = tools,
        icon = 'tool.png'
        ).initialize(context)

    profile_registry.registerProfile(
        name = 'bika',
        title = 'Bika LIMS',
        description = 'Extension profile for default Bika LIMS setup.',
        path = 'profiles/default',
        product = 'bika',
        profile_type = EXTENSION,
        for_ = IPloneSiteRoot)
