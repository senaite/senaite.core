"""BIKA - A lab information management system

$Id: __init__.py 2580 2010-12-03 19:11:40Z anneline $
"""
from Products.Archetypes.atapi import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.utils import ContentInit, ToolInit
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.GenericSetup import EXTENSION, profile_registry
from zope.i18nmessageid import MessageFactory
import logging

bikaMessageFactory = MessageFactory('Products.bika')

from config import PROJECTNAME
from content import *
import AnalysisRequest, Contact, Sample, Attachment, Analysis, \
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
import tools

logger = logging.getLogger('Bika')

import AccessControl
AccessControl.ModuleSecurityInfo('pdb').declarePublic('set_trace')


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

    toolset = (
        tools.bika_services,
        tools.bika_analysisspecs,
        tools.bika_arprofiles,
        tools.bika_products,
        tools.bika_methods,
        tools.bika_instruments,
        tools.bika_client_status,
        tools.bika_client_categories,
        tools.bika_publication_prefs,
        tools.bika_invoice_prefs,
        tools.bika_sampletypes,
        tools.bika_standardmanufacturers,
        tools.bika_standardstocks,
        tools.bika_samplepoints,
        tools.bika_worksheettemplates,
        tools.bika_labinfo,
        tools.bika_attachmenttypes,
        tools.bika_calctypes,
        tools.bika_categories,
        tools.bika_departments,
        tools.bika_labcontacts,
        tools.bika_settings,
        tools.bika_portal_ids,
        tools.bika_instrument_import,
        tools.bika_ar_import,
        tools.bika_ar_export,
        tools.bika_services_export,
        tools.bika_profiles_export,
        tools.bika_pdf_build,
        tools.bika_analysis_reset,
    )

    ToolInit(
        PROJECTNAME + ' Tools',
        tools = toolset,
        icon = 'tool.png'
        ).initialize(context)

    profile_registry.registerProfile(
        name = 'bika',
        title = 'Bika LIMS',
        product = 'bika',
        description = 'Extension profile for default Bika LIMS setup.',
        path = 'profiles/default',
        profile_type = EXTENSION,
        for_ = IPloneSiteRoot)
