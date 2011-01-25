from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from Products.bika.tools import ToolFolder
from Products.bika.interfaces.tools import Ibika_analysisspecs
from five import grok
      
class bika_analysisspecs(ToolFolder):
    """ Container for lab analysis specifications """

    grok.implements(Ibika_analysisspecs)

    security = ClassSecurityInfo()
    id = 'bika_analysisspecs'
    title = 'Lab analysis specifications'
    description = 'Set up the laboratory analysis service results specifications'
    meta_type = 'Bika Analysis Specs Tool'
    managed_portal_type = 'LabAnalysisSpec'
    listing_schema = None 
    default_template = 'labanalysisspecs' 

InitializeClass(bika_analysisspecs)
