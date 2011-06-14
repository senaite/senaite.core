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
from bika.lims.config import ADD_CONTENT_PERMISSION, BIKA_PERMISSIONS, \
    SKINS_DIR, GLOBALS, PROJECTNAME
from config import PROJECTNAME

from zope.i18nmessageid import MessageFactory
bikaMessageFactory = MessageFactory('bika')
ploneMessageFactory = MessageFactory('plone')

import logging
logger = logging.getLogger('Bika')

from content import *
from controlpanel.bika_analysiscategories import AnalysisCategories
from controlpanel.bika_analysisservices import AnalysisServices
from controlpanel.bika_labarprofiles import LabARProfiles
from controlpanel.bika_attachmenttypes import AttachmentTypes
from controlpanel.bika_calculationtypes import CalculationTypes
from controlpanel.bika_departments import Departments
from controlpanel.bika_instruments import Instruments
from controlpanel.bika_labanalysisspecs import LabAnalysisSpecs
from controlpanel.bika_labcontacts import LabContacts
from controlpanel.bika_methods import Methods
from controlpanel.bika_labproducts import LabProducts
from controlpanel.bika_samplepoints import SamplePoints
from controlpanel.bika_sampletypes import SampleTypes
from controlpanel.bika_standardmanufacturers import StandardManufacturers
from controlpanel.bika_standardstocks import StandardStocks
from controlpanel.bika_worksheettemplates import WorksheetTemplates

import AccessControl
import DuplicateAnalysis
import RejectAnalysis
import StandardAnalysis
import SupplierContact
import ClientStatus
import ClientPublicationPreference
import ClientInvoicePreference
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

registerDirectory(SKINS_DIR, GLOBALS)

allow_module('bika.lims.stats')
allow_module('bika.lims.pstat')
allow_module('whrandom')
allow_module('math')
allow_module('re')
allow_module('bika.lims.fixSchema')
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
