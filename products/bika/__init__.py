"""BIKA - A lab information management system

$Id: __init__.py 2580 2010-12-03 19:11:40Z anneline $

"""
from AccessControl import ModuleSecurityInfo, allow_module
from Products.Archetypes.atapi import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.utils import ContentInit, ToolInit, getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.GenericSetup import EXTENSION, profile_registry
from Products.bika.config import ADD_CONTENT_PERMISSION, BIKA_PERMISSIONS, \
    SKINS_DIR, GLOBALS, PROJECTNAME
from config import PROJECTNAME
from zope.i18nmessageid import MessageFactory
bikaMessageFactory = MessageFactory('bika')
ploneMessageFactory = MessageFactory('plone')

from content import *

import Organisation
import Person
import AccessControl
import AnalysisRequest
import Sample
import Analysis
import ARProfile
import ARImport
import ARImportItem
import Order
import OrderItem
import Worksheet
import WorksheetFolder
import DuplicateAnalysis
import RejectAnalysis
import StandardSupplierFolder
import StandardSupplier
import StandardSample
import StandardAnalysis
import SupplierContact
import LabAnalysisSpec
import LabARProfile
import LabProduct
import ClientCategory
import ClientStatus
import ClientPublicationPreference
import ClientInvoicePreference
import StandardManufacturer
import StandardStock
import WorksheetTemplate
import FixedPointField
import AnalysesField
import AnalysesWidget
import ReferenceBrowserListingWidget
import InvoiceFolder
import InvoiceBatch
import Invoice
import InvoiceLineItem
import MethodFolder
import MethodLogEntry
import PricelistFolder
import Pricelist
import PricelistLineItem
import logging
import tools



logger = logging.getLogger('Bika')



#OrderWorkflow
#AnalysisWorkflow
#SampleWorkflow
#StandardSampleWorkflow
#ARImportWorkflow
#WorksheetWorkflow
#WorksheetAnalysisWorkflow
#StandardAnalysisWorkflow


#ModuleSecurityInfo('Products.bika.Extensions.post_plone_install').declarePublic('run')

registerDirectory(SKINS_DIR, GLOBALS)

allow_module('Products.bika.stats')
allow_module('Products.bika.pstat')
allow_module('whrandom')
allow_module('math')
allow_module('re')
allow_module('Products.bika.fixSchema')
AccessControl.ModuleSecurityInfo('pdb').declarePublic('set_trace')

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
