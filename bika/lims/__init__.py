from AccessControl import ModuleSecurityInfo, allow_module
from Products.Archetypes.atapi import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.utils import ContentInit, ToolInit, getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.GenericSetup import EXTENSION, profile_registry
from bika.lims.config import *

from zope.i18nmessageid import MessageFactory
bikaMessageFactory = MessageFactory('bika')
ploneMessageFactory = MessageFactory('plone')

import logging
logger = logging.getLogger('Bika')

from content import *
from controlpanel import *

allow_module('bika.lims')
#allow_module('bika.lims.stats')
#allow_module('bika.lims.pstat')
#allow_module('whrandom')
#allow_module('math')
#allow_module('re')
#allow_module('bika.lims.fixSchema')
#AccessControl.ModuleSecurityInfo('pdb').declarePublic('set_trace')

def initialize(context):

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

